#!/usr/bin/env python3
"""
Comprehensive testing for Stage 2: Machine Code Generation
"""

import os
import sys
import tempfile
import subprocess


def run_assembler(input_file, output_file, test_mode=False):
    """Run assembler and get result"""
    cmd = [sys.executable, 'assembler.py', input_file, output_file]
    if test_mode:
        cmd.append('--test')

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result


def run_interpreter(binary_file, verbose=False):
    """Run interpreter and get result"""
    cmd = [sys.executable, 'interpreter.py', binary_file]
    if verbose:
        cmd.append('--verbose')

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result


def test_specific_sequences():
    """Test specific byte sequences from specification"""

    print("=" * 70)
    print("TESTING STAGE 2: MACHINE CODE GENERATION")
    print("=" * 70)

    # Test cases from specification
    test_cases = [
        {
            'name': 'LOAD_CONST 468',
            'code': 'load 468',
            'expected': bytes([0x4A, 0xD4, 0x01, 0x00, 0x00]),
            'description': 'Load constant 468 (0x1D4)'
        },
        {
            'name': 'READ_MEM 15',
            'code': 'read 15',
            'expected': bytes([0x87, 0x0F]),
            'description': 'Read from memory with offset 15'
        },
        {
            'name': 'WRITE_MEM 224',
            'code': 'write 224',
            'expected': bytes([0xD5, 0xE0, 0x00, 0x00, 0x00]),
            'description': 'Write to memory at address 224'
        },
        {
            'name': 'SGN',
            'code': 'sgn',
            'expected': bytes([0x9A]),
            'description': 'Unary operation sgn()'
        }
    ]

    all_passed = True

    for test_case in test_cases:
        print(f"\n{'=' * 60}")
        print(f"Test: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"{'=' * 60}")

        # Create temporary file with code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False, encoding='utf-8') as f:
            f.write(test_case['code'])
            input_file = f.name

        output_file = tempfile.NamedTemporaryFile(suffix='.bin', delete=False).name

        try:
            # Run assembler
            result = run_assembler(input_file, output_file, test_mode=True)

            if result.returncode != 0:
                print(f"✗ Assembly error:")
                print(result.stderr)
                all_passed = False
                continue

            # Read binary file
            with open(output_file, 'rb') as f:
                actual = f.read()

            # Check result
            if actual == test_case['expected']:
                print("✓ TEST PASSED")

                # Show byte representation
                hex_bytes = [f'0x{b:02X}' for b in actual]
                print(f"Bytes: {', '.join(hex_bytes)}")

                # Check assembler output for command count
                if "Assembled commands: 1" in result.stdout:
                    print("✓ Correct command count output")
                else:
                    print("✗ Command count not displayed correctly")

            else:
                print("✗ TEST FAILED")
                print(f"Expected: {test_case['expected'].hex()}")
                print(f"Got:      {actual.hex()}")
                all_passed = False

            # Show assembler output
            print("\nAssembler output summary:")
            print("-" * 40)
            lines = result.stdout.strip().split('\n')
            for line in lines[:5]:  # Show first 5 lines
                if line.strip():
                    print(line)

        except Exception as e:
            print(f"✗ Exception: {e}")
            all_passed = False
        finally:
            # Clean up temporary files
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    # Test file with all commands
    print(f"\n{'=' * 70}")
    print("TESTING FILE WITH ALL COMMANDS")
    print(f"{'=' * 70}")

    # Create file with all test commands
    all_commands_code = """# Test 1: Load constant 468
load 468

# Test 2: Read from memory offset 15
read 15

# Test 3: Write to memory address 224
write 224

# Test 4: Unary operation sgn
sgn
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False, encoding='utf-8') as f:
        f.write(all_commands_code)
        all_commands_file = f.name

    output_file = tempfile.NamedTemporaryFile(suffix='.bin', delete=False).name

    try:
        # Run assembler
        result = run_assembler(all_commands_file, output_file, test_mode=True)

        if result.returncode != 0:
            print(f"✗ Complex file assembly error:")
            print(result.stderr)
            all_passed = False
        else:
            # Read binary file
            with open(output_file, 'rb') as f:
                actual = f.read()

            # Expected sequence of all tests
            expected_all = (
                    bytes([0x4A, 0xD4, 0x01, 0x00, 0x00]) +  # load 468
                    bytes([0x87, 0x0F]) +  # read 15
                    bytes([0xD5, 0xE0, 0x00, 0x00, 0x00]) +  # write 224
                    bytes([0x9A])  # sgn
            )

            if actual == expected_all:
                print("✓ COMPLEX TEST PASSED")

                # Show byte representation
                hex_bytes = [f'0x{b:02X}' for b in actual]
                print(f"Full byte sequence:")
                print(", ".join(hex_bytes))

                # Check command count output
                if "Assembled commands: 4" in result.stdout:
                    print("✓ Correct command count: 4")
                else:
                    print("✗ Incorrect command count")

            else:
                print("✗ COMPLEX TEST FAILED")
                print(f"Expected: {expected_all.hex()}")
                print(f"Got:      {actual.hex()}")
                all_passed = False

    except Exception as e:
        print(f"✗ Exception: {e}")
        all_passed = False
    finally:
        # Clean up
        os.unlink(all_commands_file)
        if os.path.exists(output_file):
            os.unlink(output_file)

    print(f"\n{'=' * 70}")
    if all_passed:
        print("ALL STAGE 2 TESTS PASSED SUCCESSFULLY! ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print(f"{'=' * 70}")

    return all_passed


def test_interpreter():
    """Test interpreter with sample program"""
    print(f"\n{'=' * 70}")
    print("TESTING INTERPRETER WITH SAMPLE PROGRAM")
    print(f"{'=' * 70}")

    # Create a sample program
    sample_program = """# Sample program to test interpreter
# Load some values
load 100
load 200

# Write value 42 to address 300
load 42
write 300

# Read back from address 300
load 300
read 0

# Check sign of value at address 50
load 50
sgn
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False, encoding='utf-8') as asm_file:
        asm_file.write(sample_program)
        asm_path = asm_file.name

    bin_path = tempfile.NamedTemporaryFile(suffix='.bin', delete=False).name

    try:
        # Assemble program
        print("\n1. Assembling program...")
        asm_result = run_assembler(asm_path, bin_path)

        if asm_result.returncode != 0:
            print("✗ Assembly failed:")
            print(asm_result.stderr)
            return False

        print("✓ Program assembled successfully")

        # Run interpreter
        print("\n2. Running interpreter...")
        int_result = run_interpreter(bin_path, verbose=True)

        if int_result.returncode != 0:
            print("✗ Interpreter failed:")
            print(int_result.stderr)
            return False

        print("✓ Interpreter executed successfully")

        # Show interpreter output
        print("\nInterpreter output:")
        print("-" * 50)
        lines = int_result.stdout.split('\n')
        for i, line in enumerate(lines[:30]):  # Show first 30 lines
            print(line)
        if len(lines) > 30:
            print("... (output truncated)")

        return True

    except Exception as e:
        print(f"✗ Exception: {e}")
        return False
    finally:
        # Clean up
        for path in [asm_path, bin_path]:
            if os.path.exists(path):
                os.unlink(path)


def create_example_programs():
    """Create example programs for demonstration"""

    examples_dir = "example_programs"
    os.makedirs(examples_dir, exist_ok=True)

    # Example 1: Simple program
    example1 = """# Simple UVM program
# Load constant 100 to stack
load 100

# Read value from memory at address 100+5=105
read 5

# Load value 42
load 42

# Write it to address 200
write 200

# Check sign of value at address 150
load 150
sgn
"""

    # Example 2: Different number formats
    example2 = """# Different number formats
# Decimal number
load 100

# Hexadecimal number (0x64 = 100)
load 0x64

# Binary number (0b1100100 = 100)
load 0b1100100

# Read with small offset
read 10

# Write to large address
write 0x1000

# sgn operation
sgn
"""

    # Example 3: All commands test (matching specification)
    example3 = """# All commands test (matches specification tests)
# LOAD_CONST 468
load 468

# READ_MEM 15
read 15

# WRITE_MEM 224
write 224

# SGN
sgn
"""

    # Write examples
    examples = {
        "simple.asm": example1,
        "formats.asm": example2,
        "spec_tests.asm": example3
    }

    for filename, content in examples.items():
        with open(os.path.join(examples_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"\nCreated example programs in folder '{examples_dir}':")
    for filename in examples.keys():
        print(f"  - {filename}")


def quick_direct_test():
    """Quick direct test without files"""
    print("\n" + "=" * 70)
    print("QUICK DIRECT TEST (no files)")
    print("=" * 70)

    try:
        # Import modules directly
        from assembler import Assembler, Opcode, Instruction

        tests = [
            ("LOAD_CONST 468", Instruction(Opcode.LOAD_CONST, 468, 1),
             bytes([0x4A, 0xD4, 0x01, 0x00, 0x00])),
            ("READ_MEM 15", Instruction(Opcode.READ_MEM, 15, 1),
             bytes([0x87, 0x0F])),
            ("WRITE_MEM 224", Instruction(Opcode.WRITE_MEM, 224, 1),
             bytes([0xD5, 0xE0, 0x00, 0x00, 0x00])),
            ("SGN", Instruction(Opcode.SGN, None, 1),
             bytes([0x9A])),
        ]

        all_pass = True

        for name, instr, expected in tests:
            print(f"\nTesting {name}:")
            assembler = Assembler()
            assembler.instructions = [instr]
            binary = assembler.assemble_to_binary()

            if binary == expected:
                print(f"✓ PASS - Bytes: {binary.hex()}")
            else:
                print(f"✗ FAIL")
                print(f"  Expected: {expected.hex()}")
                print(f"  Got:      {binary.hex()}")
                all_pass = False

        print("\n" + "=" * 70)
        if all_pass:
            print("ALL DIRECT TESTS PASSED ✓")
        else:
            print("SOME DIRECT TESTS FAILED ✗")
        print("=" * 70)

        return all_pass

    except Exception as e:
        print(f"Error in quick test: {e}")
        return False


if __name__ == '__main__':
    # Run quick direct test first
    print("Starting comprehensive test suite...")

    if quick_direct_test():
        print("\nProceeding to full test suite...")

        # Run main tests
        if test_specific_sequences():
            print("\nProceeding to interpreter test...")

            # Test interpreter
            if test_interpreter():
                print("\n" + "=" * 70)
                print("ALL TESTS COMPLETED SUCCESSFULLY!")
                print("=" * 70)

                # Create example programs
                create_example_programs()

                # Final message
                print("\n" + "=" * 70)
                print("STAGE 2 IMPLEMENTATION COMPLETE")
                print("=" * 70)
                print("\nSummary of implemented features:")
                print("1. ✓ Machine code generation for all instructions")
                print("2. ✓ Binary file output")
                print("3. ✓ Command count display")
                print("4. ✓ Test mode with byte output")
                print("5. ✓ All specification test sequences verified")
                print("6. ✓ Working interpreter")
                print("=" * 70)
            else:
                print("\nInterpreter test failed")
                sys.exit(1)
        else:
            print("\nMain tests failed")
            sys.exit(1)
    else:
        print("\nQuick test failed")
        sys.exit(1)