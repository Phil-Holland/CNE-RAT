# API Documentation

This document describes the required format of the JSON POST request data submitted to create new CNE-Finder jobs and CNEAT analyses.

Each API route is validated against a schema, using [json-schema](https://json-schema.org/).

Detailed documentation is generated using [jsonschema2md](https://github.com/adobe/jsonschema2md).

## CNE-Finder

## CNEAT

**API endpoint**: `/new_analysis`

### Example request:

```json
{
    "cne": ">cne\nACGTACGTACGTACGT",
    "rna_protein": true,
    "rna_protein_config": {
        "drosophila_melanogaster": true,
        "homo_sapiens": true,
        "mus_musculus": false
    },
    "rna_rna": true,
    "rna_rna_config": {
        "inta": true,
        "inta_config": {
            "prediction_mode": "M",
            "minpu": 0.5
        },
        "query_sequences": ">query1\nCCCCGGGGAAAATTTT",
        "vienna": true,
        "vienna_config": {
            "rnaduplex": true,
            "rnaduplex_config": {
                "deltaenergy": 5
            },
            "rnacofold": true
        }
    }
}
```

### Detailed request documentation: **[cneat.md](cneat.md)**

### Response

- **HTTP code `400`:** returned if a validation error has been encountered.
  - Response data: a JSON object, with the following properties:
    - `success`: always `false` for a `400` response.
    - `error`: a string describing the error.
- **HTTP code `200`:** returned if the request was successful.
  - Response data: a JSON object, with the following properties:
    - `success`: always `true` for a `200` response.
    - `uid`: a string containing the **unique analysis identifier**.