
# CNEAT Schema

```
cneat
```

A schema defining a CNEAT analysis configuration

| Abstract | Extensible | Status | Identifiable | Custom Properties | Additional Properties | Defined In |
|----------|------------|--------|--------------|-------------------|-----------------------|------------|
| Can be instantiated | No | Experimental | No | Forbidden | Permitted | [cneat.schema.json](cneat.schema.json) |

# CNEAT Properties

| Property | Type | Required | Nullable | Defined by |
|----------|------|----------|----------|------------|
| [cne](#cne) | `string` | **Required**  | No | CNEAT (this schema) |
| [rna_protein](#rna_protein) | `boolean` | **Required**  | No | CNEAT (this schema) |
| [rna_protein_config](#rna_protein_config) | `object` | Optional  | No | CNEAT (this schema) |
| [rna_rna](#rna_rna) | `boolean` | **Required**  | No | CNEAT (this schema) |
| [rna_rna_config](#rna_rna_config) | `object` | Optional  | No | CNEAT (this schema) |
| `*` | any | Additional | Yes | this schema *allows* additional properties |

## cne

A string holding the CNE sequence in FASTA format

`cne`

* is **required**
* type: `string`
* defined in this schema

### cne Type


`string`

* minimum length: 1 characters





## rna_protein

A boolean representing whether or not the RNA-protein analysis pipeline should be executed

`rna_protein`

* is **required**
* type: `boolean`
* defined in this schema

### rna_protein Type


`boolean`





## rna_protein_config

Additional configuration options for the RNA-protein analysis pipeline - required if 'rna_protein' is true

`rna_protein_config`

* is optional
* type: `object`
* defined in this schema

### rna_protein_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `drosophila_melanogaster`| boolean | **Required** |
| `homo_sapiens`| boolean | **Required** |
| `mus_musculus`| boolean | **Required** |



#### drosophila_melanogaster

A boolean representing whether or not Drosophila melanogaster is relevant in this analysis

`drosophila_melanogaster`

* is **required**
* type: `boolean`

##### drosophila_melanogaster Type


`boolean`







#### homo_sapiens

A boolean representing whether or not Homo sapiens is relevant in this analysis

`homo_sapiens`

* is **required**
* type: `boolean`

##### homo_sapiens Type


`boolean`







#### mus_musculus

A boolean representing whether or not Mus musculus is relevant in this analysis

`mus_musculus`

* is **required**
* type: `boolean`

##### mus_musculus Type


`boolean`










## rna_rna

A boolean representing whether or not the RNA-RNA analysis pipeline should be executed

`rna_rna`

* is **required**
* type: `boolean`
* defined in this schema

### rna_rna Type


`boolean`





## rna_rna_config

Additional configuration options for the RNA-protein analysis pipeline - required if 'rna_rna' is true

`rna_rna_config`

* is optional
* type: `object`
* defined in this schema

### rna_rna_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `inta`| boolean | **Required** |
| `inta_config`| object | Optional |
| `query_sequences`| string | **Required** |
| `vienna`| boolean | **Required** |
| `vienna_config`| object | Optional |



#### inta

A boolean representing whether or not the IntaRNA pipeline should be executed

`inta`

* is **required**
* type: `boolean`

##### inta Type


`boolean`







#### inta_config

Additional configuration options for the IntaRNA analysis pipeline - required if 'inta' is true

`inta_config`

* is optional
* type: `object`

##### inta_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `minpu`| number | **Required** |
| `prediction_mode`| string | **Required** |



#### minpu

A float representing minimum unpaired probability of returned results

`minpu`

* is **required**
* type: `number`

##### minpu Type


`number`

* minimum value: `0`
* maximum value: `1`







#### prediction_mode

The mode of prediction used by the IntaRNA executable (H=heuristic, M=exact)

`prediction_mode`

* is **required**
* type: `enum`

The value of this property **must** be equal to one of the [known values below](#rna_rna_config-known-values).

##### prediction_mode Known Values
| Value | Description |
|-------|-------------|
| `H` |  |
| `M` |  |











#### query_sequences

A string holding the query sequence(s) in FASTA format

`query_sequences`

* is **required**
* type: `string`

##### query_sequences Type


`string`

* minimum length: 1 characters







#### vienna

A boolean representing whether or not the ViennaRNA pipeline should be executed

`vienna`

* is **required**
* type: `boolean`

##### vienna Type


`boolean`







#### vienna_config

Additional configuration options for the ViennaRNA analysis pipeline - required if 'vienna' is true

`vienna_config`

* is optional
* type: `object`

##### vienna_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `rnacofold`| boolean | **Required** |
| `rnaduplex`| boolean | **Required** |
| `rnaduplex_config`| object | Optional |



#### rnacofold

A boolean representing whether or not the RNAcofold executable should be run

`rnacofold`

* is **required**
* type: `boolean`

##### rnacofold Type


`boolean`







#### rnaduplex

A boolean representing whether or not the RNAduplex executable should be run

`rnaduplex`

* is **required**
* type: `boolean`

##### rnaduplex Type


`boolean`







#### rnaduplex_config

Additional configuration options for the RNAduplex executable - required if 'rnaduplex' is true

`rnaduplex_config`

* is optional
* type: `object`

##### rnaduplex_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `deltaenergy`| number | **Required** |



#### deltaenergy

A float representing the energy range for returned sub-optimal interactions, in kcal/mol

`deltaenergy`

* is **required**
* type: `number`

##### deltaenergy Type


`number`

* minimum value: `0`






















**One** of the following *conditions* need to be fulfilled.


#### Condition 1



#### Condition 2



#### Condition 3


