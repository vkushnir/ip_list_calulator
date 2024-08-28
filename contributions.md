# Contributions

## GitHub

GitHub serves applications from multiple IP address ranges, which are available using the API.
You can retrieve a list of GitHub's IP addresses from the [meta](https://api.github.com/meta) API endpoint. For more information, see "[REST API endpoints for meta data](https://docs.github.com/en/rest/meta)."

[About GitHub's IP addresses](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses)

## RIPE

[Country Resource List](https://stat.ripe.net/docs/02.data-api/country-resource-list.html)

This data call lists the Internet resources associated with a country, including ASNs, IPv4 ranges and IPv4/6 CIDR prefixes.

This data is derived from the RIR Statistics files maintained by the various RIRs.

```
GET /data/country-resource-list/data.json?resource=at&time=2020-12-01
```

### Parameters
| Key       | Value                                                                                                                                                      | Info                                                                                                   | Required            |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------|:--------------------|
| resource  | 2-digit ISO-3166 country code (e.g. "at","de"...)                                                                                                          | The country to find IP prefixes and AS numbers for.                                                    | YES                 |
| time      | ISO8601 or Unix timestamp                                                                                                                                  | The time to query. By default, returns the latest available data. This value is truncated to midnight. | NO                  |
| v4_format | format parameter; possible values: "" or "prefix". "prefix" will return each entry in prefix notation, meaning that ranges are converted to CIDR prefixes. | Describes the formatting for the output of IPv4 space.                                                 | NO. Defaults to ""  |

# Data Output

| Key                                      | Info                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|:-----------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| resources                                | <table><caption>Lists of resources that are associated with the queried country according to the RIR stats files.</cation><tr><td>asn</td><td>A sorted list of ASN numbers associated with the queried country.</td></tr><tr><td>ipv4</td><td>A sorted list of IPv4 prefixes and/or ranges associated with the queried country.</td></tr><tr><td>ipv6</td><td>A sorted list of IPv6 prefixes associated with the queried country.</td></tr></table> |
| query_time                               | The time covered by the query.resourceThe resource used for the query.                                                                                                                                                                                                                                                                                                                                                                              |
| resource                                 | The resource used for the query.                                                                                                                                                                                                                                                                                                                                                                                                                    |

```shell
curl --location --request GET "https://stat.ripe.net/data/country-resource-list/data.json?resource=at&time=2020-12-01"
```

