#!/usr/bin/env python3
"""
Interpreter for Educational Virtual Machine (UVM) - Stage 3: Separate Memory Model
"""

import sys
import struct
import argparse
import json
from typing import List, Dict, Any


class UVMInterpreter:
    """UVM Interpreter with separate code and data memory"""

    def __init__(self, data_memory_size: int = 1024):
        # Code memory: loaded from binary file (read-only for execution)
        self.code_memory: bytes = b""
        self.program_size = 0

        # Data memory: for read/write operations (1 KB by default)
        self.data_memory = bytearray(data_memory_size)

        # Stack for operations
        self.stack: List[int] = []

        # Instruction pointer (for code memory)
        self.ip = 0

    def load_program(self, binary_data: bytes):
        """Load binary program into code memory"""
        self.code_memory = binary_data
        self.program_size = len(binary_data)
        print(f"Loaded {self.program_size} bytes of program into code memory")

    def read_byte_from_code(self) -> int:
        """Read next byte from code memory"""
        if self.ip >= self.program_size:
            raise RuntimeError("Instruction pointer beyond program end")
        byte = self.code_memory[self.ip]
        self.ip += 1
        return byte

    def read_dword_from_code(self) -> int:
        """Read 4-byte little-endian value from code memory"""
        if self.ip + 4 > self.program_size:
            raise RuntimeError("Not enough bytes to read DWORD from code")
        value = struct.unpack('<I', self.code_memory[self.ip:self.ip + 4])[0]
        self.ip += 4
        return value

    def push(self, value: int):
        """Push to stack"""
        self.stack.append(value)

    def pop(self) -> int:
        """Pop from stack"""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def execute(self, verbose: bool = False):
        """Main interpretation loop"""
        print("\n" + "=" * 60)
        print("UVM INTERPRETER (Stage 3) STARTING")
        print("Memory model: separate code and data")
        print("=" * 60)

        instruction_count = 0

        while self.ip < self.program_size:
            start_ip = self.ip
            opcode = self.read_byte_from_code()
            instruction_count += 1

            if verbose:
                print(f"\n[{instruction_count}] IP=0x{start_ip:04X}: ", end="")

            if opcode == 74:  # LOAD_CONST
                constant = self.read_dword_from_code()
                self.push(constant)
                if verbose:
                    print(f"LOAD_CONST({constant}) → stack={self.stack}")

            elif opcode == 135:  # READ_MEM
                offset_byte = self.read_byte_from_code()
                offset = offset_byte & 0x3F  # 6 bits
                base_addr = self.pop()
                addr = base_addr + offset
                if not (0 <= addr < len(self.data_memory)):
                    raise RuntimeError(f"READ_MEM: invalid data address {addr}")
                value = self.data_memory[addr]
                self.push(value)
                if verbose:
                    print(f"READ_MEM(base={base_addr}, offset={offset}) → data[{addr}]={value} → stack={self.stack}")

            elif opcode == 213:  # WRITE_MEM
                addr = self.read_dword_from_code()
                value = self.pop() & 0xFF
                if not (0 <= addr < len(self.data_memory)):
                    raise RuntimeError(f"WRITE_MEM: invalid data address {addr}")
                self.data_memory[addr] = value
                if verbose:
                    print(f"WRITE_MEM(data[{addr}] = {value})")

            elif opcode == 154:  # SGN
                addr = self.pop()
                if not (0 <= addr < len(self.data_memory)):
                    raise RuntimeError(f"SGN: invalid data address {addr}")
                byte_val = self.data_memory[addr]
                # Interpret as signed byte
                signed_val = struct.unpack('<b', bytes([byte_val]))[0]
                if signed_val > 0:
                    result = 1
                elif signed_val < 0:
                    result = -1
                else:
                    result = 0
                self.push(result)
                if verbose:
                    print(f"SGN(data[{addr}] = {signed_val}) → {result} → stack={self.stack}")

            else:
                raise RuntimeError(f"Unknown opcode: 0x{opcode:02X} at IP=0x{start_ip:04X}")

        print(f"\nExecution finished. Instructions executed: {instruction_count}")

    def save_memory_dump(self, filepath: str, start: int, end: int):
        """Save data memory dump to JSON"""
        if start < 0 or end > len(self.data_memory) or start > end:
            raise ValueError(f"Invalid memory range: [{start}, {end})")

        dump_data = {}
        for addr in range(start, end):
            dump_data[str(addr)] = self.data_memory[addr]

        output = {
            "memory_dump": {
                "start": start,
                "end": end,
                "size": end - start,
                "data": dump_data
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Data memory dump saved to: {filepath} (addresses {start}-{end-1})")


def main():
    parser = argparse.ArgumentParser(description='UVM Interpreter - Stage 3')
    parser.add_argument('binary_file', help='Path to binary program file')
    parser.add_argument('--dump', help='Path to JSON memory dump file')
    parser.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'),
                        default=[0, 256],
                        help='Range of data memory addresses to dump (default: 0 256)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose execution output')

    args = parser.parse_args()

    try:
        # Load program
        with open(args.binary_file, 'rb') as f:
            binary_data = f.read()

        print(f"Reading program: {args.binary_file} ({len(binary_data)} bytes)")

        # Initialize and run interpreter
        interpreter = UVMInterpreter(data_memory_size=1024)
        interpreter.load_program(binary_data)
        interpreter.execute(args.verbose)

        # Save memory dump if requested
        if args.dump:
            start, end = args.range
            interpreter.save_memory_dump(args.dump, start, end)

        # Show final stack
        print(f"\nFinal stack: {interpreter.stack}")

    except Exception as e:
        print(f"Execution error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()