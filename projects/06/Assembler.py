import os
import re
import sys

class Parser:
    """Encapsulates access to the input code"""
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3

    def __init__(self, infile):
        """Opens the input file/stream and gets ready to parse it"""
        self.commands = []
        for line in infile:
            line = re.sub('\/\/.*\n|\n|\s+', '', line)
            if line:
                self.commands.append(line)
        self.current = 0
        self.command = None

    def has_more_commands(self):
        """Are there more commands in the input?"""
        return self.current != len(self.commands)

    def advance(self):
        """Reads the next command from the input and makes it the
        current command. Should be called only if has_more_commands()
        is True. Initially there is no current command."""
        self.command = self.commands[self.current]
        self.current += 1

    def command_type(self):
        """Returns the type of the current command"""
        if self.command[0] == '@':
            return Parser.A_COMMAND
        if self.command[0] == '(':
            return Parser.L_COMMAND
        return Parser.C_COMMAND

    def symbol(self):
        """Returns the symbol or decimal Xxx of the current command
        @Xxx or (Xxx). Should be called only when command_type() is
        A_COMMAND or L_COMMAND."""
        if self.command_type() == Parser.A_COMMAND:
            return self.command[1:]
        elif self.command_type() == Parser.L_COMMAND:
            return self.command[1:-1]
        return None

    def dest(self):
        """Returns the dest mnemonic in the current C-command. Should
        be called only when command_type() is C_COMMAND."""
        match = re.search('(.*=)?([^;]+)(;.*)?', self.command)
        if match:
            if match[1]:
                return match[1][:-1]
            return ''
        return None

    def comp(self):
        """Returns the comp mnemonic in the current C-command. Should
        be called only when command_type() is C_COMMAND."""
        match = re.search('(.*=)?([^;]+)(;.*)?', self.command)
        if match:
            return match[2]
        return None

    def jump(self):
        """Returns the jump mnemonic in the current C-command. Should
        be called only when command_type() is C_COMMAND."""
        match = re.search('(.*=)?([^;]+)(;.*)?', self.command)
        if match:
            if match[3]:
                return match[3][1:]
            return ''
        return None


class Code:
    def __init__(self):
        self.dest_bits = {
                '': '000',
                'M': '001',
                'D': '010',
                'MD': '011',
                'A': '100',
                'AM': '101',
                'AD': '110',
                'AMD': '111'}
        self.comp_bits = {
                '0':   '0101010',
                '1':   '0111111',
                '-1':  '0111010',
                'D':   '0001100',
                'A':   '0110000',
                'M':   '1110000',
                '!D':  '0001101',
                '!A':  '0110001',
                '!M':  '1110001',
                '-D':  '0001111',
                '-A':  '0110011',
                '-M':  '1110011',
                'D+1': '0011111',
                'A+1': '0110111',
                'M+1': '1110111',
                'D-1': '0001110',
                'A-1': '0110010',
                'M-1': '1110010',
                'D+A': '0000010',
                'D+M': '1000010',
                'D-A': '0010011',
                'D-M': '1010011',
                'A-D': '0000111',
                'M-D': '1000111',
                'D&A': '0000000',
                'D&M': '1000000',
                'D|A': '0010101',
                'D|M': '1010101'}

        self.jump_bits = {
                '':    '000',
                'JGT': '001',
                'JEQ': '010',
                'JGE': '011',
                'JLT': '100',
                'JNE': '101',
                'JLE': '110',
                'JMP': '111'}

    def dest(self, mnemonic):
        """Returns the binary code of the dest mnemonic."""
        return self.dest_bits[mnemonic]

    def comp(self, mnemonic):
        """Returns the binary code of the comp mnemonic."""
        return self.comp_bits[mnemonic]

    def jump(self, mnemonic):
        """Returns the binary code of the jump mnemonic."""
        return self.jump_bits[mnemonic]


class SymbolTable:
    def __init__(self):
        """Create a new empty symbol table"""
        self.symbols = dict()

    def add_entry(self, symbol, address):
        """Adds the pair (symbol, address) to the table."""
        self.symbols[symbol] = address

    def contains(self, symbol):
        """Does the symbol table contain the given symbol?"""
        return symbol in self.symbols

    def get_address(self, symbol):
        """Returns the address associated with symbol."""
        return self.symbols[symbol]


def first_pass(infile):
    symbols = SymbolTable()
    symbols.add_entry('SP', 0)
    symbols.add_entry('LCL', 1)
    symbols.add_entry('ARG', 2)
    symbols.add_entry('THIS', 3)
    symbols.add_entry('THAT', 4)
    for i in range(16):
        symbols.add_entry('R' + str(i), i)
    symbols.add_entry('SCREEN', 16384)
    symbols.add_entry('KBD', 24576)

    parser = Parser(infile)
    address = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() != Parser.L_COMMAND:
            address += 1
        else:
            symbol = parser.symbol()
            symbols.add_entry(symbol, address)
    return symbols

def second_pass(infile, symbols, filename):
    parser = Parser(infile)
    code = Code()
    outfile = open(filename, 'w')
    address = 16
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == Parser.C_COMMAND:
            outfile.write('111')
            outfile.write(code.comp(parser.comp()))
            outfile.write(code.dest(parser.dest()))
            outfile.write(code.jump(parser.jump()))
            outfile.write('\n')
        elif parser.command_type() == Parser.A_COMMAND:
            outfile.write('0')
            symbol = parser.symbol()
            if symbol.isdigit():
                outfile.write(format(int(symbol), '015b'))
            elif symbols.contains(symbol):
                outfile.write(format(int(symbols.get_address(symbol)), '015b'))
            else:
                symbols.add_entry(symbol, address)
                outfile.write(format(address, '015b'))
                address += 1
            outfile.write('\n')
    outfile.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage: Assembler <file>")
    filename = sys.argv[1]
    infile = open(filename, 'r')
    symbols = first_pass(infile)
    infile.seek(0)
    second_pass(infile, symbols, os.path.splitext(filename)[0] + '.hack')
    infile.close()
