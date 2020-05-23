# python intepreter 

This is an interpreter for a programming langauge that is very similar to Python. Below is some examples for how it works.

> (+ 3 2)

  => 5


> (define (square x) (* x x))

  => FUNCTION: (lambda (x) (* x x))


> (define (fourthpower x) (square (square x)))

  => FUNCTION: (lambda (x) (square (square x)))


> (fourthpower 1.1)

  => 1.4641000000000004


> (+ 3 (- 7 8))

  => 2
  
  
  The interpreter consists of three parts: 
  
1- A tokenizer, which takes a string as input and produces a list of tokens

2- A parser, which takes the output of the tokenizer as input and produces a structured representation of the program as its output.

3- An evaluator, which takes the output of the parser as input and handles running the program.
