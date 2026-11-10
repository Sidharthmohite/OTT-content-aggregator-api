
# Title Module Field Documentation

| Field | Type | Description |
|---|---|---|
| id | Integer | Unique title ID |
| title | String | Movie or series name |
| description | Text | Content description |
| content_type | String | movie or web_series |
| release_year | Integer | Release year |
| language | String | Content language |
| duration_minutes | Integer | Movie duration |
| number_of_seasons | Integer | Number of seasons |
| created_at | DateTime | Creation date |

## Movie
- content_type: movie
- duration_minutes: Required
- number_of_seasons: null

## Web Series
- content_type: web_series
- duration_minutes: null
- number_of_seasons: Required
- duration_minutes: 148
- number_of_seasons: null

## Web Series
- duration_minutes: null
- number_of_seasons: 5

## Relationships
Genre and OTT Platform relationships
will be coordinated with M5.
## Validation
- Title must not be empty.
- Content type must be movie or web_series.
- Release year must be valid.
- Duration and number of seasons must be positive when provided.

## M4 Module Files
- src/models/title.py
- src/schemas/title.py
- src/api/titles.py
- src/services/catalog_service.py

## Testing Status
Testing and integration are pending verification. 
