from tmdl.lexer import lex_tmdl, TokenType


def test_model_lexer():
    input_text = """model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3
	sourceQueryCulture: en-US
	dataAccessOptions
		legacyRedirects
		returnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBIDesktopVersion = 2.103.661.0 (22.03)

annotation PBI_QueryOrder = ["HttpSource","Customer","Date","Product","Reseller","Sales","Sales Order","Sales Territory"]

ref table Customer
ref table Date
ref table Product
ref table Reseller
ref table Sales
ref table 'Sales Order'
ref table 'Sales Territory'"""

    tokens = lex_tmdl(input_text)

    # Basic validation of token sequence
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "model"

    # Print tokens for debugging
    for token in tokens:
        print(f"{token.type}: {token.value}")
