# python intepreter 

This is an interpreter for a programming langauge that is very similar to Python

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
