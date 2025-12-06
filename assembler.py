#!/usr/bin/env python3
"""
Assembler for Educational Virtual Machine (UVM) - Stage 2: Machine Code Generation
"""

import sys
import argparse
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

# Check for PyYAML
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class Opcode(Enum):
    """UVM operation codes"""
    LOAD_CONST = 74  # Load constant
    READ_MEM = 135  # Read from memory
    WRITE_MEM = 213  # Write to memory
    SGN = 154  # Unary operation sgn()

    @classmethod
    def from_mnemonic(cls, mnemonic: str) -> 'Opcode':
        """Convert mnemonic to opcode"""
        mapping = {
            'load': cls.LOAD_CONST,
            'read': cls.READ_MEM,
            'write': cls.WRITE_MEM,
            'sgn': cls.SGN
        }
        if mnemonic.lower() not in mapping:
            raise ValueError(f"Unknown mnemonic: {mnemonic}")
        return mapping[mnemonic.lower()]


@dataclass
class Instruction:
    """Instruction representation"""
    opcode: Opcode
    operand: Optional[int] = None
    line_number: int = 0  # Line number in source file

    def to_binary(self) -> bytes:
        """Convert instruction to binary representation"""
        if self.opcode == Opcode.LOAD_CONST:
            # 5 bytes: A(1) + B(4) - constant
            if self.operand is None:
                raise ValueError(f"Line {self.line_number}: LOAD requires operand")
            return self.opcode.value.to_bytes(1, 'little') + \
                self.operand.to_bytes(4, 'little')

        elif self.opcode == Opcode.READ_MEM:
            # 2 bytes: A(1) + B(1) - offset (6 bits)
            if self.operand is None:
                raise ValueError(f"Line {self.line_number}: READ requires operand")
            if self.operand > 0x3F:  # 6 bits
                raise ValueError(f"Line {self.line_number}: Offset too large: {self.operand}. Max 63.")
            return self.opcode.value.to_bytes(1, 'little') + \
                self.operand.to_bytes(1, 'little')

        elif self.opcode == Opcode.WRITE_MEM:
            # 5 bytes: A(1) + B(4) - address
            if self.operand is None:
                raise ValueError(f"Line {self.line_number}: WRITE requires operand")
            return self.opcode.value.to_bytes(1, 'little') + \
                self.operand.to_bytes(4, 'little')

        elif self.opcode == Opcode.SGN:
            # 1 byte: only A
            return self.opcode.value.to_bytes(1, 'little')

        else:
            raise ValueError(f"Line {self.line_number}: Unknown opcode: {self.opcode}")

    def get_size(self) -> int:
        """Get instruction size in bytes"""
        if self.opcode == Opcode.LOAD_CONST:
            return 5
        elif self.opcode == Opcode.READ_MEM:
            return 2
        elif self.opcode == Opcode.WRITE_MEM:
            return 5
        elif self.opcode == Opcode.SGN:
            return 1
        return 0


class Assembler:
    """UVM Assembler"""

    def __init__(self):
        self.instructions: List[Instruction] = []
        self.binary_data: bytes = b''

    def parse_yaml(self, yaml_content: Dict[str, Any]) -> None:
        """Parse YAML program representation"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML not installed. Install: pip install pyyaml")

        if 'program' not in yaml_content:
            raise ValueError("YAML must contain 'program' key")

        for i, instr_data in enumerate(yaml_content['program']):
            if 'op' not in instr_data:
                raise ValueError(f"Instruction {i + 1} must contain 'op' key")

            mnemonic = instr_data['op']
            opcode = Opcode.from_mnemonic(mnemonic)

            operand = instr_data.get('operand')
            if operand is not None:
                # Convert string number representations
                if isinstance(operand, str):
                    if operand.startswith('0x'):
                        operand = int(operand, 16)
                    elif operand.startswith('0b'):
                        operand = int(operand, 2)
                    else:
                        operand = int(operand)

            instruction = Instruction(opcode, operand, i + 1)
            self.instructions.append(instruction)

    def parse_simple_text(self, filepath: str) -> None:
        """Parse simple text format (YAML alternative)"""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Remove inline comments
            if '#' in line:
                line = line.split('#')[0].strip()

            parts = line.split()
            if len(parts) < 1:
                continue

            mnemonic = parts[0].lower()
            try:
                opcode = Opcode.from_mnemonic(mnemonic)
            except ValueError as e:
                raise ValueError(f"Line {line_num}: {e}")

            operand = None
            if len(parts) > 1:
                operand_str = parts[1]
                try:
                    if operand_str.startswith('0x'):
                        operand = int(operand_str, 16)
                    elif operand_str.startswith('0b'):
                        operand = int(operand_str, 2)
                    else:
                        operand = int(operand_str)
                except ValueError:
                    raise ValueError(f"Line {line_num}: Invalid operand format: {operand_str}")

            instruction = Instruction(opcode, operand, line_num)
            self.instructions.append(instruction)

    def assemble_to_binary(self) -> bytes:
        """Assemble to binary format"""
        self.binary_data = b''
        for instr in self.instructions:
            try:
                self.binary_data += instr.to_binary()
            except ValueError as e:
                raise ValueError(str(e))
        return self.binary_data

    def get_internal_representation(self) -> List[Dict[str, Any]]:
        """Get internal program representation"""
        internal_repr = []

        for instr in self.instructions:
            instr_dict = {
                'opcode': instr.opcode.name,
                'opcode_value': instr.opcode.value,
                'operand': instr.operand,
                'size': instr.get_size(),
                'line': instr.line_number
            }

            # Add description
            if instr.opcode == Opcode.LOAD_CONST:
                instr_dict['description'] = 'Load constant'
            elif instr.opcode == Opcode.READ_MEM:
                instr_dict['description'] = 'Read from memory'
            elif instr.opcode == Opcode.WRITE_MEM:
                instr_dict['description'] = 'Write to memory'
            elif instr.opcode == Opcode.SGN:
                instr_dict['description'] = 'Unary operation sgn()'

            internal_repr.append(instr_dict)

        return internal_repr

    def display_binary_output(self, format_style: str = 'hex') -> str:
        """Display binary program representation in specified format"""
        if not self.binary_data:
            self.assemble_to_binary()

        output_lines = []

        if format_style == 'hex':
            # Format as in specification: 0x4A, 0xD4, 0x01, 0x00, 0x00
            hex_bytes = [f'0x{b:02X}' for b in self.binary_data]
            output_lines.append(", ".join(hex_bytes))

        elif format_style == 'detailed':
            # Detailed output with instruction breakdown
            byte_offset = 0
            for i, instr in enumerate(self.instructions):
                instr_bytes = instr.to_binary()
                hex_bytes = [f'0x{b:02X}' for b in instr_bytes]
                output_lines.append(f"Instruction {i} (line {instr.line_number}): {', '.join(hex_bytes)}")
                byte_offset += len(instr_bytes)

        return "\n".join(output_lines)

    def save_binary_file(self, filepath: str) -> None:
        """Save binary file"""
        if not self.binary_data:
            self.assemble_to_binary()

        with open(filepath, 'wb') as f:
            f.write(self.binary_data)


def main():
    parser = argparse.ArgumentParser(
        description='Assembler for Educational Virtual Machine (UVM) - Stage 2'
    )
    parser.add_argument('input_file', help='Path to source file (.yaml, .yml, .asm, .txt)')
    parser.add_argument('output_file', help='Path to binary output file')
    parser.add_argument('--test', action='store_true',
                        help='Test mode (display internal representation)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    try:
        assembler = Assembler()

        # Determine file format by extension
        _, ext = os.path.splitext(args.input_file)

        if ext.lower() in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                print("Error: PyYAML not installed.")
                print("Install: pip install pyyaml")
                print("Or use text format (.asm)")
                sys.exit(1)

            # Read YAML file
            with open(args.input_file, 'r', encoding='utf-8') as f:
                yaml_content = yaml.safe_load(f)
            assembler.parse_yaml(yaml_content)

        elif ext.lower() in ['.asm', '.txt']:
            # Read simple text file
            assembler.parse_simple_text(args.input_file)

        else:
            print("Error: unknown file format. Use .yaml, .yml, .asm or .txt")
            sys.exit(1)

        # Assemble to binary format
        binary_data = assembler.assemble_to_binary()

        # Display number of assembled commands
        num_instructions = len(assembler.instructions)
        print(f"Assembled commands: {num_instructions}")
        print(f"Total program size: {len(binary_data)} bytes")

        if args.test or args.verbose:
            print("\n" + "=" * 60)
            print("INTERNAL PROGRAM REPRESENTATION:")
            print("=" * 60)

            internal_repr = assembler.get_internal_representation()
            total_size = 0

            for i, instr in enumerate(internal_repr):
                print(f"\nInstruction {i} (line {instr['line']}):")
                print(f"  Mnemonic: {instr['opcode']}")
                print(f"  Opcode: {instr['opcode_value']} (0x{instr['opcode_value']:02X})")
                print(f"  Operand: {instr['operand']}")
                print(f"  Size: {instr['size']} bytes")
                print(f"  Description: {instr['description']}")

                # Display binary representation of this instruction
                instr_binary = assembler.instructions[i].to_binary()
                hex_bytes = [f'0x{b:02X}' for b in instr_binary]
                print(f"  Bytes: {', '.join(hex_bytes)}")

                total_size += instr['size']

            print(f"\nTotal size: {total_size} bytes")

        if args.test:
            print("\n" + "=" * 60)
            print("BYTE REPRESENTATION OF PROGRAM (specification format):")
            print("=" * 60)
            print(assembler.display_binary_output('hex'))

        # Save binary file
        assembler.save_binary_file(args.output_file)

        print(f"\nProgram successfully saved to: {args.output_file}")

    except Exception as e:
        print(f"Assembly error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()