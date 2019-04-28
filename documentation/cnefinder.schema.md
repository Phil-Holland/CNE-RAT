
# CNEFinder Schema

```
cnefinder
```

A schema defining a CNEFinder run configuration

| Abstract | Extensible | Status | Identifiable | Custom Properties | Additional Properties | Defined In |
|----------|------------|--------|--------------|-------------------|-----------------------|------------|
| Can be instantiated | No | Experimental | No | Forbidden | Permitted | [cnefinder.schema.json](cnefinder.schema.json) |

# CNEFinder Properties

| Property | Type | Required | Nullable | Defined by |
|----------|------|----------|----------|------------|
| [ensembl_request_config](#ensembl_request_config) | `object` | **Required**  | No | CNEFinder (this schema) |
| [gene_name](#gene_name) | `boolean` | **Required**  | No | CNEFinder (this schema) |
| [gene_name_config](#gene_name_config) | `object` | **Required**  | No | CNEFinder (this schema) |
| [general_config](#general_config) | `object` | **Required**  | No | CNEFinder (this schema) |
| [index_position](#index_position) | `boolean` | **Required**  | No | CNEFinder (this schema) |
| [index_position_config](#index_position_config) | `object` | **Required**  | No | CNEFinder (this schema) |
| `*` | any | Additional | Yes | this schema *allows* additional properties |

## ensembl_request_config

Configuration options for the requests that will be made to the user-submitted ensembl sites

`ensembl_request_config`

* is **required**
* type: `object`
* defined in this schema

### ensembl_request_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `query_dataset`| string | **Required** |
| `query_mart`| string | **Required** |
| `query_site`| string | **Required** |
| `ref_dataset`| string | **Required** |
| `ref_mart`| string | **Required** |
| `ref_site`| string | **Required** |



#### query_dataset

A string holding the name of the ensembl dataset containing the query genome

`query_dataset`

* is **required**
* type: `string`

##### query_dataset Type


`string`









#### query_mart

A string holding the name of the ensembl BioMart containing the query genome

`query_mart`

* is **required**
* type: `string`

##### query_mart Type


`string`









#### query_site

A string holding the URL of the ensembl site/archive containing the query genome

`query_site`

* is **required**
* type: `string`

##### query_site Type


`string`









#### ref_dataset

A string holding the name of the ensembl dataset containing the reference genome

`ref_dataset`

* is **required**
* type: `string`

##### ref_dataset Type


`string`









#### ref_mart

A string holding the name of the ensembl BioMart containing the reference genome

`ref_mart`

* is **required**
* type: `string`

##### ref_mart Type


`string`









#### ref_site

A string holding the URL of the ensembl site/archive containing the reference genome

`ref_site`

* is **required**
* type: `string`

##### ref_site Type


`string`












## gene_name

A boolean representing whether CNFinder should search for CNEs based on gene names

`gene_name`

* is **required**
* type: `boolean`
* defined in this schema

### gene_name Type


`boolean`





## gene_name_config

Additional configuration options for a gene-name-focussed CNEFinder run

`gene_name_config`

* is **required**
* type: `object`
* defined in this schema

### gene_name_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `query_gene_name`| string | **Required** |
| `ref_gene_name`| string | **Required** |



#### query_gene_name

A string holding the URL of the name of chosen gene within the query genome

`query_gene_name`

* is **required**
* type: `string`

##### query_gene_name Type


`string`









#### ref_gene_name

A string holding the URL of the name of chosen gene within the reference genome

`ref_gene_name`

* is **required**
* type: `string`

##### ref_gene_name Type


`string`












## general_config

Task-agnostic configuration options for a CNEFinder run

`general_config`

* is **required**
* type: `object`
* defined in this schema

### general_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `min_cne_length`| number | **Required** |
| `sim_threshold`| number | **Required** |



#### min_cne_length

A number holding the minimum CNE length CNEFinder will search for

`min_cne_length`

* is **required**
* type: `number`

##### min_cne_length Type


`number`

* minimum value: `1`
* must be a multiple of `1`







#### sim_threshold

A number holding the similarity threshold defining matching CNE regions

`sim_threshold`

* is **required**
* type: `number`

##### sim_threshold Type


`number`

* minimum value: `0`
* maximum value: `1`
* must be a multiple of `0.01`










## index_position

A boolean representing whether CNFinder should search for CNEs based on index positions

`index_position`

* is **required**
* type: `boolean`
* defined in this schema

### index_position Type


`boolean`





## index_position_config

Additional configuration options for a index-positon-focussed CNEFinder run

`index_position_config`

* is **required**
* type: `object`
* defined in this schema

### index_position_config Type


`object` with following properties:


| Property | Type | Required |
|----------|------|----------|
| `query_chromosome`| number | **Required** |
| `query_end_pos`| number | **Required** |
| `query_start_pos`| number | **Required** |
| `ref_chromosome`| number | **Required** |
| `ref_end_pos`| number | **Required** |
| `ref_start_pos`| number | **Required** |



#### query_chromosome

A number holding the chromosome on the query genome to be searched

`query_chromosome`

* is **required**
* type: `number`

##### query_chromosome Type


`number`

* minimum value: `1`
* maximum value: `100`
* must be a multiple of `1`







#### query_end_pos

A number holding the end index on the query genome to be searched

`query_end_pos`

* is **required**
* type: `number`

##### query_end_pos Type


`number`

* minimum value: `0`
* must be a multiple of `1`







#### query_start_pos

A number holding the start index on the query genome to be searched

`query_start_pos`

* is **required**
* type: `number`

##### query_start_pos Type


`number`

* minimum value: `0`
* must be a multiple of `1`







#### ref_chromosome

A number holding the chromosome on the reference genome to be searched

`ref_chromosome`

* is **required**
* type: `number`

##### ref_chromosome Type


`number`

* minimum value: `1`
* maximum value: `100`
* must be a multiple of `1`







#### ref_end_pos

A number holding the end index on the reference genome to be searched

`ref_end_pos`

* is **required**
* type: `number`

##### ref_end_pos Type


`number`

* minimum value: `0`
* must be a multiple of `1`







#### ref_start_pos

A number holding the start index on the reference genome to be searched

`ref_start_pos`

* is **required**
* type: `number`

##### ref_start_pos Type


`number`

* minimum value: `0`
* must be a multiple of `1`











**Any** following *options* needs to be fulfilled.


#### Option 1



#### Option 2


