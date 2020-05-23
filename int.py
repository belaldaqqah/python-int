#!/usr/bin/env python3



class EvaluationError(Exception):
    """
    Exception to be raised if there is an error during evaluation other than a
    NameError.
    """
    pass



def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    result = []
    
    for word in source.splitlines():
        current_word = ""
        while word:
            letter = word[0]        
            
            if letter == "(" or letter == ")":
                if current_word != "":
                    result.append(current_word)
                result.append(letter)
                current_word = ""
        
            elif letter == " ":
                if current_word != "":
                    result.append(current_word)
                current_word = ""
                
            elif letter == ";":
                if current_word != "":
                    result.append(current_word)
                break 
            
            else:
                current_word += letter 
                #last letter
                if len(word) == 1: 
                    result.append(current_word )
                  

            word = word[1:]

    return result
        


def parse(tokens):
    
    def parse_expression(index): 
        result = [] 
        
                
        if tokens[index] == ")": 
            raise SyntaxError
        
        if tokens[index] != "(": 
            try: 
                try: 
                    return int(tokens[index]), index + 1 
                except:
                    return float(tokens[index]), index + 1 
            except:
                return tokens[index], index + 1 
            

            
        next_index = index + 1 
        while tokens[next_index] != ")":
            parsed, next_index = parse_expression(next_index)
            result += [parsed]
            #if no ")" has been found: 
            if next_index == len(tokens): 
                raise SyntaxError
                
        return result, next_index + 1 
    
    parsed_expression, next_index = parse_expression(0)
    if next_index != len(tokens): 
        raise SyntaxError
    return parsed_expression

          
def division(list_): 
    if len(list_) == 1: 
        return int(list_) 
    num = list_[0]
    for i in range(len(list_)-1): 
        num = num/list_[i+1]
        
    return num


class Environment: 
    def __init__(self, parent = None):
        self.variables = {}
        self.parent = parent 
        self.children = None
          
    def set_variable(self, x, val):
        """
        set a variable given it's name and assignment, by putting it in a dictionary
        """
        self.variables[x] = val 
            
            
    def get_variable(self, x):
        """
        return the value of a given variable by looking up into the dictionary of variables 
        of the current environment. If it's not there look up into the variables of parent envrionments.
        Raise NameError if it's eventually not found
        """
        if x in self.variables: 
            return self.variables[x]
        else: 
            try:
                return self.get_parent().get_variable(x) 
            except:
                raise NameError
                
  
    def get_parent(self):
        """
        return the parent of the global environment 
        """
        return self.parent 
    

class Function: 
    def __init__(self, parameters, environment, body): 
        #we create a new environemnt, whose parent is the parent environment
        self.parameters = parameters
        self.environment = environment
        self.body = body
        

    def get_evaluated(self, arguments):
        """"
        Given arguments, evaluate the function using the values of those arguments by assigning them
        to the parameters in the current environment and returning the evaluated value.
        If there's more or less arguments than parameters then raise an EvaluationError.
        """
        
        if len(arguments) > len(self.parameters) or len(arguments) < len(self.parameters):
            raise EvaluationError

        for param, arg in zip(self.parameters, arguments): 
            self.environment.set_variable(param, arg)

        return evaluate(self.body, self.environment)
        
        #bind the arguments to the current environment 
        
    def is_function(self): 
        return True 
            
        

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': lambda args: args[0] if len(args) ==1 else (args[0] * carlae_builtins['*'](args[1:])), 
    '/': division, 
    'define': lambda tree, environment: define(tree, environment), 
    'lambda': lambda tree, environment: Function(tree[1], Environment(environment),  tree[2])

}


#setting up the builtin environment 
builtin_env = Environment()
for key in carlae_builtins: 
    builtin_env.set_variable(key, carlae_builtins[key])
    
    
global_env = Environment(builtin_env)


def define(tree, environment):
    """
    if the first work of the tree is define, then define that variable or function in the same envrionemnt
    If it's a function then return the function back 
    If it's a variable, then return it's value back 
    """
    #if the assiggment is one element
    if len(tree[2:]) == 1: 
        to_evaluate = tree[2]    
    #if the assignment is an expression
    else: 
        to_evaluate = tree[2:]
        
    #defining functions 
    if type(tree[1]) == list: 
        parameters = tree[1][1:]
        #create a child envrionemnt and define the function inside it 
        function = Function(parameters, Environment(environment), to_evaluate)
        environment.set_variable(tree[1][0], function)
        return function
    
    #we assign the variable to the result of evaluating the sub-expression in the environment
    environment.set_variable(tree[1], evaluate(to_evaluate, environment))
    #we get the variable from the environment
    return environment.get_variable(tree[1])

def evaluate(tree, environment = Environment(builtin_env)):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    
    final_eq = []

    #base case: if the tree is one element and not a list
    if type(tree) != list: 
        if type(tree) == str:
            #we look up if it's either an operation, or a variable in our environment, and raise a NameError otherwise
            try: 
                return environment.get_variable(tree) 
            except:
                raise NameError
        elif type(tree) == int or type(tree) == float: 
            return tree 
    else: 
        
        if tree[0] == 'define': 
            return define(tree, environment)

        #defining a new funciton 
        if tree[0] == 'lambda': 
            #evaluate all of the arguments to the function in the current environment (from which the function is being called)
            #if tree[3] exists this means it has given its arguments:
            return Function(tree[1], Environment(environment),  tree[2])
          
        #create a boolean value, that help us keep track if we have a defined function 
        defined_func = False
        
        try: 
            #check if we have a variable
            t = environment.get_variable(tree[0])
            #check if that variable is a function 
            try:
                defined_func = t.is_function() 
            except: 
                pass
        except:
            #inline_lambda (e.g. ((lambda (x) (* x x)) 3))
            if type(tree[0]) == list: 
                func = evaluate(tree[0], environment)
                args = tree[1:]
                return func.get_evaluated(args)
            
            #check if it's not one of the built-ins 
            if tree[0] not in carlae_builtins: 
                raise EvaluationError()
            
            
        for elm in tree: 
            #if the element is a list, we implement the function recursively on this function
            if type(elm) == list: 
                elm = evaluate(elm, environment)  
                final_eq.append(elm)
                
            else:
                #if the element is not a builtin, or int or float, then it might be a variable, so we called the getter function
                if not isinstance(elm, (int, float)) and elm not in carlae_builtins: 
                    #then elm is a variable 
                    elm = environment.get_variable(elm)
                final_eq.append(elm)
                
                
        if defined_func: 
            func = environment.get_variable(tree[0])
            return func.get_evaluated(final_eq[1:])

        #we get the function from our global environment, which looks for it in the built-in environment
        try: 
            func = environment.get_variable(final_eq[0])
        #ptherwise, it might be already a function in our result
        except: 
            func = final_eq[0]
    
        return func(final_eq[1:])
    
    
def result_and_env(tree, environment = None ): 
    """
    takes the same arguments as evaluate but returns a tuple with two elements:
    the result of the evaluation and the environment in which the expression
    was ultimately evaluated.
    """
    #if the environment is not specified, make a new one 
    if environment == None: 
        environment = Environment(builtin_env)
    return evaluate(tree, environment), environment


    
if __name__ == '__main__':

    end_word = 'quit'
    print('Type quit to stop.')
    inp = ""

    while inp != end_word:
        inp = input('in> ')
        if inp != end_word:
            try:
                tokens = tokenize(inp)
                parsed = parse(tokens)
                print('out> ', str(evaluate(parsed)))
            except: 
                print("There was an error in your statement")
           
