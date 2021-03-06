#! env/bin/python

import sys, re, pdb, json

class TokenType(object):
  TYPE_INT = 'TYPE_INT'
  TYPE_VOID = 'TYPE_VOID'
  INT = 'INT'
  ID = 'ID'
  BRACKET_LEFT = 'BRACKET_LEFT'
  BRACKET_RIGHT = 'BRACKET_RIGHT'
  BRACE_LEFT = 'BRACE_LEFT'
  BRACE_RIGHT = 'BRACE_RIGHT'
  SEMI_COLON = 'SEMI_COLON'
  IF = 'IF'
  ELSE = 'ELSE'
  RETURN = 'RETURN'
  LT_EQ = 'LT_EQ'
  LT = 'LT'
  GT = 'GT'
  GT_EQ = 'GT_EQ'
  EQ_EQ = 'EQ_EQ'
  N_EQ = 'N_EQ'
  WHILE = 'WHILE'
  EQ = 'EQ'
  OP_MUL = 'OP_MUL'
  OP_ADD = 'OP_ADD'
  OP_DIV = 'OP_DIV'
  OP_SUB = 'OP_SUB'
  COMMENT_START = 'COMMENT_START'
  COMMENT_END = 'COMMENT_END'
  PARENTHESES_RIGHT = 'PARENTHESES_RIGHT'
  PARENTHESES_LEFT = 'PARENTHESES_LEFT'
  COMMA = "COMMA"

token_type_num = {
  'TYPE_INT' : 0,
  'TYPE_VOID' : 1,
  'INT' : 2,
  'ID' : 3,
  'BRACKET_LEFT' : 4,
  'BRACKET_RIGHT' : 5,
  'BRACE_LEFT' : 6,
  'BRACE_RIGHT' : 7,
  'SEMI_COLON' : 8,
  'IF' : 9,
  'ELSE' : 10,
  'RETURN' : 11,
  'LT_EQ' : 12,
  'LT' : 13,
  'GT' : 14,
  'GT_EQ' : 15,
  'EQ_EQ' : 16,
  'N_EQ' : 17,
  'WHILE' : 18,
  'EQ' : 19,
  'OP_MUL' : 20,
  'OP_ADD' : 21,
  'OP_DIV' : 22,
  'OP_SUB' : 23,
  'COMMENT_START' : 24,
  'COMMENT_END' : 25,
  'PARENTHESES_RIGHT' : 26,
  'PARENTHESES_LEFT' : 27,
  'COMMA' : 28
}

token_types = {
  ';':    TokenType.SEMI_COLON,
  'int':  TokenType.TYPE_INT,
  'void': TokenType.TYPE_VOID,
  '}':    TokenType.BRACE_LEFT,
  '{':    TokenType.BRACE_RIGHT,
  ']':    TokenType.BRACKET_LEFT,
  '[':    TokenType.BRACKET_RIGHT,
  'if':   TokenType.IF,
  'else': TokenType.ELSE,
  'return': TokenType.RETURN,
  '<=':   TokenType.LT_EQ,
  '<':    TokenType.LT,
  '>':    TokenType.GT,
  '>=':   TokenType.GT_EQ,
  '==':   TokenType.EQ_EQ,
  '!=':   TokenType.N_EQ,
  '=':    TokenType.EQ,
  'while':TokenType.WHILE,
  '*':    TokenType.OP_MUL,
  '+':    TokenType.OP_ADD,
  '-':    TokenType.OP_SUB,
  '/':    TokenType.OP_DIV,
  ')':    TokenType.PARENTHESES_LEFT,
  '(':    TokenType.PARENTHESES_RIGHT,
  '/*':   TokenType.COMMENT_START,
  '*/':   TokenType.COMMENT_END,
  ',':    TokenType.COMMA
}

class Token(object):
  def __init__(self, token_type, value):
    self.Type = token_type
    self.Value = value 

def is_letter(string):
  return re.match('[a-zA-Z_]*', string)

def is_numeric(string):
  return re.match('[0-9]+', string)

def is_valid_id(string):
  return re.match('[a-zA-Z][a-zA-Z0-9_]*$', string)

class Tokenizer(object):
  def __init__(self):
    self.token_str = ''
    self.state = "NOT_READING" #READING_ID | READING_INT | READING_KEYWORD | NOT_READING | COMMENT
    self.result_tokens = []
    self.prevChar = ''

  def consume_character(self, pos, src):
    #check to see if a comment has been entered or exited

    char = src[pos]
    
    if pos+1 < len(src):
      if self.state != 'COMMENT':
        if char == '/' and src[pos+1] == '*':
          #grab the token that was being formed (if valid)
          self.state = 'COMMENT'
      else:
        if char == '/' and  self.prevChar == '*':
          self.state = 'NOT_READING'
          return

    if self.state != 'COMMENT':
      if char == ' ' or char == '\n' or char == '\t':
        if self.state == 'READING_ID':
          if is_valid_id(self.token_str):
            self.result_tokens.append(Token(TokenType.ID, self.token_str))
            self.state = 'NOT_READING'
            self.token_str = ''
          else:
            raise Exception('invalid token ' + self.token_str)
        elif self.state == 'READING_INT':
          if self.token_str.isdigit():
            self.result_tokens.append(Token(TokenType.INT, self.token_str))
            self.state = 'NOT_READING'
            self.token_str = ''
          else:
            raise Exception('invalid token ' + self.token_str)
        elif self.state == 'READING_KEYWORD':
          if self.token_str in token_types.keys():
            self.result_tokens.append(Token(token_types[self.token_str], self.token_str))
          else:
            self.result_tokens.append(Token(TokenType.ID, self.token_str))

          self.state = 'NOT_READING'
          self.token_str = ''
        elif self.state == 'NOT_READING':
          pass
      else:
        if self.state == 'READING_ID':
          if is_valid_id(self.token_str + char):
            self.state = 'READING_ID'
            self.token_str += char
          else:
            #emit the ID token (token_str)
            self.result_tokens.append(Token(TokenType.ID, self.token_str))

            #if char is a root:
            if Tokenizer.is_root(char):
              self.state = 'READING_KEYWORD'
              self.token_str = char
            elif char.isdigit():
              self.state = 'READING_INT'
              self.token_str = char
            else:
              raise Exception("Invalid token: " + token_str)

        elif self.state == 'READING_INT':
          #if char is an int:
          if char.isdigit():
            self.token_str += char
          elif Tokenizer.is_root(char):
            self.result_tokens.append(Token(TokenType.INT, self.token_str))
            self.token_str = char
            self.state = 'READING_KEYWORD'
          else:
            raise Exception("invalid token: " + self.token_str)

        elif self.state == 'READING_KEYWORD':

          if Tokenizer.is_root(self.token_str+char):
            self.token_str += char
          elif is_valid_id(self.token_str+char):
            self.token_str += char
            self.state = 'READING_ID'
            #State <- READING_ID
          else:
            #if token_str is a keyword:
            if self.token_str in token_types.keys():
              self.result_tokens.append(Token(token_types[self.token_str], self.token_str))
              #emit keyword token
            elif is_valid_id(self.token_str):
              self.result_tokens.append(Token(TokenType.ID, self.token_str))
              
              if Tokenizer.is_root(char):
                self.token_str = char
                self.state = 'READING_KEYWORD'
              else:
                raise Exception("invalid token: "+self.token_str)

            else:
              raise Exception("incomplete keyword: " + self.token_str)
              #error condition (incomplete keyword)

            if Tokenizer.is_root(char):
              self.state = 'READING_KEYWORD'
              self.token_str = char
            elif char.isalpha():
              self.state = 'READING_ID'
              self.token_str = char
            elif char.isdigit():
              self.state = 'READING_INT'
              self.token_str = char

        elif self.state == 'NOT_READING':
            if Tokenizer.is_root(char):
              self.state = 'READING_KEYWORD'
              self.token_str = char
            elif char.isalpha():
              self.state = 'READING_ID'
              self.token_str = char
            elif char.isdigit():
              self.state = 'READING_INT'

              self.token_str = char
    self.prevChar = char
    
  def Tokenize(self, src):
    for i in range(0, len(src)):
      self.consume_character(i, src)

    return self.result_tokens

  @staticmethod
  def token_is_alphanumeric(token_str):
    if re.match('[0-9]+', token_str):
      return True
    elif re.match('[a-zA-Z][a-zA-Z0-9_]*', token_str):
      return True
    else:
      return False

  @staticmethod
  def is_root(token_str):
    result =  map(lambda x: x.startswith(token_str), token_types.keys())
    for x in result:
      if x:
        return True
    
    return False

  @staticmethod
  def is_only_root(token_str):
    result =  map(lambda x: x.startswith(token_str), token_types.keys())
    result = map(lambda x: 1 if x else 0, result)
    for x in result:
      if x:
        result = True
        break
    
    return result == 1

  @staticmethod
  def match_keyword_token(token_str):
    if token_str in token_types.keys():
      return Token(token_types[token_str], token_str)
  
  @staticmethod
  def match_id_int_token(token_str):
    if re.match('[0-9]+', token_str):
      return Token(TokenType.INT, token_str)
    elif re.match('[a-zA-Z][a-zA-Z0-9_]*', token_str):
      return Token(TokenType.ID, token_str)
    else:
      return None
    
  @staticmethod
  def match_token(token_str):
    if not Tokenizer.token_is_root(token_str):
      return None
    else:
      if re.match('[0-9]+', token_str):
        return Token(TokenType.INT, token_str)
      elif re.match('[a-zA-Z][a-zA-Z0-9_]*', token_str):
        return Token(TokenType.ID, token_str)
      else:
        print("somethings fucky")
        return None

  @staticmethod
  def token_pp(token):
    print('\nName: {0}, Value: {1}\n'.format(token.Type, token.Value))

  @staticmethod
  def print_tokens(tokens):
    for token in tokens:
      Tokenizer.token_pp(token)

  @staticmethod
  def store_tokens_json(output, tokens):
    tokens_json = map(lambda x: {'Type': token_type_num[x.Type], 'Value': x.Value}, tokens)

    with open(output, 'w') as f:
      pdb.set_trace()
      json.dump(tokens_json, f)

  
if __name__ == "__main__":
  with open("example.c") as f:
    src = f.read()
    tokenizer = Tokenizer()
    tokens = tokenizer.Tokenize(src) 
    Tokenizer.print_tokens(tokens)
    Tokenizer.store_tokens_json('output-tokens.json', tokens)
