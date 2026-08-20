import json
from typing import Any

from cipher_client import CipherClient


PHENOTYPE_FILTER_FIELDS = [
    "PhenotypeFullName", "PhenotypeDescription", "PhenotypeKeyword",
    "PhenotypeStatus", "PhenotypeSourceName", "PhenotypeClassificationName",
    "PhenotypeTypeCategoryName", "PhenotypeRelationType", "PhenotypeRoleType",
    "PhenotypePublicationsTitle", "AlgorithmMethodUsed", "AlgorithmAuthor",
    "AlgorithmContact", "AlgorithmContextDevelopment", "AlgorithmDesc",
    "AlgorithmRelatedDisease", "AlgorithmAssociatedCode",
    "AlgorithmAssociatedOtherCodeType", "AlgorithmAssociatedCodeType",
    "AlgorithmAssociatedSubCodeType", "AlgorithmValidated",
    "AlgorithmValidationDesc", "AlgorithmPopulationDesc",
    "PublicationAcknowledgement", "PhenotypeTextExpansion", "Any",
]

ENUM_TYPES = [
    "All", "Phenotype_Status", "Phenotype_DataClassification",
    "Phenotype_RelatedDiseaseDomain", "Algorithm_MethodUsed",
    "Algorithm_PerformanceMeasures", "Phenotype_DataSource",
    "Phenotype_AnalysisRole", "Phenotype_Lab_Specimen",
    "Algorithm_Associated_Codes", "Phenotype_Relation",
    "Phenotype_Review_Status", "Phenotype_Category",
    "Algorithm_Context_Development", "Phenotype_Attachment",
    "Algorithm_Lab_Associated_Codes", "Algorithm_Medication_Associated_Codes",
    "Algorithm_Text_Associated_Codes", "Algorithm_Programming_Language",
    "Keyword_Source", "Algorithm_Code_Lookup", "Algorithm_Level_Adjudication",
]

FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "field": {"type": "string", "enum": PHENOTYPE_FILTER_FIELDS},
        "searchField": {"type": ["string", "null"]},
        "value": {"type": "string"},
        "overrideKeyword": {"type": ["boolean", "null"]},
        "textFieldName": {"type": ["string", "null"]},
    },
    "required": ["field", "searchField", "value", "overrideKeyword", "textFieldName"],
    "additionalProperties": False,
}


def _nullable(type_name: str) -> dict[str, Any]:
    return {"type": [type_name, "null"]}


TOOLS = [
    {
        "type": "function",
        "name": "search_phenotypes",
        "description": "Search the CIPHER phenotype library. Use filters when the question names a specific phenotype or algorithm field.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                "is_validated": _nullable("boolean"),
                "has_algorithm_code": _nullable("boolean"),
                "has_publication": _nullable("boolean"),
                "has_attachment": _nullable("boolean"),
                "filters": {"type": "array", "items": FILTER_SCHEMA},
            },
            "required": ["query", "limit", "is_validated", "has_algorithm_code", "has_publication", "has_attachment", "filters"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_phenotype",
        "description": "Retrieve full details for one CIPHER phenotype by numeric system ID or UQID.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "phenotype_id": {"type": "string"},
                "revision": {"type": "string", "description": "Use latest unless a specific revision is requested."},
            },
            "required": ["phenotype_id", "revision"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "compare_phenotypes",
        "description": "Compare fields across two or more CIPHER phenotypes using the CIPHER comparison endpoint.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "base_id": {"type": "integer"},
                "compare_ids": {"type": "array", "items": {"type": "integer"}, "minItems": 1},
                "fields": {"type": "array", "items": {"type": "string"}},
                "review": {"type": "boolean"},
            },
            "required": ["base_id", "compare_ids", "fields", "review"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_variables",
        "description": "Search variables in CIPHER data dictionaries.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["query", "limit"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_dictionaries",
        "description": "Search CIPHER data dictionaries by natural-language terms.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                "has_algorithm_component": _nullable("boolean"),
            },
            "required": ["query", "limit", "has_algorithm_component"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_dictionary",
        "description": "Retrieve one CIPHER data dictionary by UQID and optionally include variables.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "uqid": {"type": "string"},
                "include_variables": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "required": ["uqid", "include_variables", "limit"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_field_values",
        "description": "Retrieve CIPHER enumeration values such as phenotype status, related disease domain, method used, data source, or code types.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"enum_type": {"type": "string", "enum": ENUM_TYPES}},
            "required": ["enum_type"],
            "additionalProperties": False,
        },
    },
]


def dispatch_tool(client: CipherClient, name: str, arguments_json: str) -> Any:
    args = json.loads(arguments_json)

    if name == "search_phenotypes":
        return client.search_phenotypes(**args)
    if name == "get_phenotype":
        return client.get_phenotype(**args)
    if name == "compare_phenotypes":
        return client.compare_phenotypes(**args)
    if name == "search_variables":
        return client.search_variables(**args)
    if name == "search_dictionaries":
        return client.search_dictionaries(**args)
    if name == "get_dictionary":
        return client.get_dictionary(**args)
    if name == "get_field_values":
        return client.get_field_values(**args)

    raise ValueError(f"Unknown tool: {name}")
