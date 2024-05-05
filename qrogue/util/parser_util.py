from antlr4.error.ErrorListener import ErrorListener

from qrogue.util.config import Config


class ParserErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # print(f"Syntax Error: \"{offendingSymbol}\" at line {line}, column {column} - {msg}")
        raise SyntaxError(msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        Config.debug_print("Ambiguity")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        Config.debug_print("Attempting full context")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        Config.debug_print("Context sensitivity")
