#!/usr/bin/env python3
"""
Быстрый запуск тестов УВМ
"""

import sys
import os


def main():
    print("Тестирование УВМ")
    print("=" * 50)

    # Тест 1: Ассемблирование test_all_commands.asm
    print("\n1. Тест ассемблирования всех команд:")
    os.system("python assembler.py test_all_commands.asm test.bin --test")

    # Тест 2: Запуск интерпретатора
    print("\n2. Тест интерпретатора:")
    os.system("python interpreter.py test.bin --verbose")

    # Тест 3: Запуск комплексного теста
    print("\n3. Комплексный тест:")
    os.system("python test_stage2.py")

    # Тест ассемблирования — spec_tests.asm (любой порядок команд)
    os.system("python assembler.py spec_tests.asm test.bin --test")

    # Тест интерпретатора — valid_test.asm (корректная логика)
    os.system("python assembler.py valid_test.asm prog.bin")
    os.system("python interpreter.py prog.bin --dump result.json --range 190 210")


if __name__ == "__main__":
    main()