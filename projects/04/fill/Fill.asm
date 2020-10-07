// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
	@SCREEN
	D=A
	@addr
	M=D

	@KBD
	D=M
	@PRESSED
	D;JEQ
	D=-1
(PRESSED)
	@color
	M=D

(RENDER)
	@addr
	D=M
	@KBD
	D=D-A
	@LOOP
	D;JGE

	@color
	D=M
	@addr
	A=M
	M=D
	D=A+1
	@addr
	M=D

	@RENDER
	0;JMP
