# ZAP Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## Summary of Alerts

| Risk Level | Number of Alerts |
| --- | --- |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational | 2 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Info | Informational | http://localhost:8000 | Percentage of responses with status code 2xx | 1 % |
| Info | Informational | http://localhost:8000 | Percentage of responses with status code 4xx | 98 % |
| Info | Informational | http://localhost:8000 | Percentage of endpoints with content type application/json | 100 % |
| Info | Informational | http://localhost:8000 | Percentage of endpoints with method GET | 63 % |
| Info | Informational | http://localhost:8000 | Percentage of endpoints with method POST | 36 % |
| Info | Informational | http://localhost:8000 | Count of total endpoints | 41    |







## Alerts

| Name | Risk Level | Number of Instances |
| --- | --- | --- |
| A Client Error response code was returned by the server | Informational | 39 |
| Non-Storable Content | Informational | Systemic |




## Alert Detail



### [ A Client Error response code was returned by the server ](https://www.zaproxy.org/docs/alerts/100000/)



##### Informational (High)

### Description

A response code of 401 was returned by the server.
This may indicate that the application is failing to handle unexpected input correctly.
Raised by the 'Alert on HTTP Response Code Error' script

* URL: http://localhost:8000
  * Node Name: `http://localhost:8000`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/
  * Node Name: `http://localhost:8000/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/830737480938024683
  * Node Name: `http://localhost:8000/830737480938024683`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/auth
  * Node Name: `http://localhost:8000/auth`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/auth/
  * Node Name: `http://localhost:8000/auth/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/auth/7082368115119473917
  * Node Name: `http://localhost:8000/auth/7082368115119473917`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/auth/actuator/health
  * Node Name: `http://localhost:8000/auth/actuator/health`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas
  * Node Name: `http://localhost:8000/multas`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/
  * Node Name: `http://localhost:8000/multas/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/10
  * Node Name: `http://localhost:8000/multas/10`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/10/
  * Node Name: `http://localhost:8000/multas/10/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/10/2827237486935431375
  * Node Name: `http://localhost:8000/multas/10/2827237486935431375`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/9157835204406176436
  * Node Name: `http://localhost:8000/multas/9157835204406176436`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios
  * Node Name: `http://localhost:8000/usuarios`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/
  * Node Name: `http://localhost:8000/usuarios/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10
  * Node Name: `http://localhost:8000/usuarios/10`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10/
  * Node Name: `http://localhost:8000/usuarios/10/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10/3085680812360422649
  * Node Name: `http://localhost:8000/usuarios/10/3085680812360422649`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10/emprestimos
  * Node Name: `http://localhost:8000/usuarios/10/emprestimos`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10/emprestimos/
  * Node Name: `http://localhost:8000/usuarios/10/emprestimos/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10/multas
  * Node Name: `http://localhost:8000/usuarios/10/multas`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/10/multas/
  * Node Name: `http://localhost:8000/usuarios/10/multas/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/4367050068863142207
  * Node Name: `http://localhost:8000/usuarios/4367050068863142207`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/auth/login
  * Node Name: `http://localhost:8000/auth/login ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: http://localhost:8000/auth/login/
  * Node Name: `http://localhost:8000/auth/login/ ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: http://localhost:8000/computeMetadata/v1/
  * Node Name: `http://localhost:8000/computeMetadata/v1/ ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/devolucoes
  * Node Name: `http://localhost:8000/devolucoes ()({exemplar_id})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `409`
  * Other Info: ``
* URL: http://localhost:8000/devolucoes
  * Node Name: `http://localhost:8000/devolucoes ()({exemplar_id})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://localhost:8000/devolucoes/
  * Node Name: `http://localhost:8000/devolucoes/ ()({exemplar_id})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `409`
  * Other Info: ``
* URL: http://localhost:8000/emprestimos
  * Node Name: `http://localhost:8000/emprestimos ()({exemplar_id})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `403`
  * Other Info: ``
* URL: http://localhost:8000/emprestimos/
  * Node Name: `http://localhost:8000/emprestimos/ ()({exemplar_id})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `403`
  * Other Info: ``
* URL: http://localhost:8000/latest/meta-data/
  * Node Name: `http://localhost:8000/latest/meta-data/ ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/metadata/instance
  * Node Name: `http://localhost:8000/metadata/instance ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/metadata/v1
  * Node Name: `http://localhost:8000/metadata/v1 ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/10/pagamento
  * Node Name: `http://localhost:8000/multas/10/pagamento`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/multas/10/pagamento/
  * Node Name: `http://localhost:8000/multas/10/pagamento/`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/opc/v1/instance/
  * Node Name: `http://localhost:8000/opc/v1/instance/ ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/opc/v2/instance/
  * Node Name: `http://localhost:8000/opc/v2/instance/ ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://localhost:8000/openstack/latest/meta_data.json
  * Node Name: `http://localhost:8000/openstack/latest/meta_data.json ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``


Instances: 39

### Solution



### Reference



#### CWE Id: [ 388 ](https://cwe.mitre.org/data/definitions/388.html)


#### WASC Id: 20

#### Source ID: 4

### [ Non-Storable Content ](https://www.zaproxy.org/docs/alerts/10049/)



##### Informational (Medium)

### Description

The response contents are not storable by caching components such as proxy servers. If the response does not contain sensitive, personal or user-specific information, it may benefit from being stored and cached, to improve performance.

* URL: http://localhost:8000/livros
  * Node Name: `http://localhost:8000/livros`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `authorization:`
  * Other Info: ``
* URL: http://localhost:8000/openapi.json
  * Node Name: `http://localhost:8000/openapi.json`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `authorization:`
  * Other Info: ``
* URL: http://localhost:8000/usuarios/eu
  * Node Name: `http://localhost:8000/usuarios/eu`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `authorization:`
  * Other Info: ``
* URL: http://localhost:8000/auth/login
  * Node Name: `http://localhost:8000/auth/login ()({email,senha})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `authorization:`
  * Other Info: ``
* URL: http://localhost:8000/emprestimos
  * Node Name: `http://localhost:8000/emprestimos ()({exemplar_id})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `authorization:`
  * Other Info: ``

Instances: Systemic


### Solution

The content may be marked as storable by ensuring that the following conditions are satisfied:
The request method must be understood by the cache and defined as being cacheable ("GET", "HEAD", and "POST" are currently defined as cacheable)
The response status code must be understood by the cache (one of the 1XX, 2XX, 3XX, 4XX, or 5XX response classes are generally understood)
The "no-store" cache directive must not appear in the request or response header fields
For caching by "shared" caches such as "proxy" caches, the "private" response directive must not appear in the response
For caching by "shared" caches such as "proxy" caches, the "Authorization" header field must not appear in the request, unless the response explicitly allows it (using one of the "must-revalidate", "public", or "s-maxage" Cache-Control response directives)
In addition to the conditions above, at least one of the following conditions must also be satisfied by the response:
It must contain an "Expires" header field
It must contain a "max-age" response directive
For "shared" caches such as "proxy" caches, it must contain a "s-maxage" response directive
It must contain a "Cache Control Extension" that allows it to be cached
It must have a status code that is defined as cacheable by default (200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501).

### Reference


* [ https://datatracker.ietf.org/doc/html/rfc7234 ](https://datatracker.ietf.org/doc/html/rfc7234)
* [ https://datatracker.ietf.org/doc/html/rfc7231 ](https://datatracker.ietf.org/doc/html/rfc7231)
* [ https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html ](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html)


#### CWE Id: [ 524 ](https://cwe.mitre.org/data/definitions/524.html)


#### WASC Id: 13

#### Source ID: 3


