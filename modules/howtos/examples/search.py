"""
= Full Text Search using the SDK
:navtitle: Full Text Search using the SDK
:page-topic-type: howto
:page-aliases: search-query
:lang: Python
:version: 3.0.0
:example-source: 3.0@python-sdk:howtos:example$search.py
:example-source-lang: Python

[abstract]
You can use the Full Text Search service (FTS) to create queryable full-text indexes in Couchbase Server.



Full Text Search or FTS allows you to create, manage, and query full text indexes on JSON documents stored in Couchbase buckets.
It uses natural language processing for querying documents, provides relevance scoring on the results of your queries, and has fast indexes for querying a wide range of possible text searches.
Some of the supported query types include simple queries like Match and Term queries; range queries like Date Range and Numeric Range; and compound queries for conjunctions, disjunctions, and/or boolean queries.
The .NET SDK exposes an API for performing FTS queries which abstracts some of the complexity of using the underlying REST API.

// As of Couchbase Server 6.5, FTS...

== Examples

Search queries are executed at Cluster level (not bucket or collection).
Here is a simple MatchQuery that looks for the text “swanky” using a defined index:
"""
# tag::imports[]
from couchbase.cluster import Cluster, ClusterOptions, PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from couchbase.search import QueryStringQuery, SearchQuery, SearchOptions, PrefixQuery, HighlightStyle, SortField, \
    SortScore, TermFacet
from couchbase.mutation_state import MutationState

import logging
# end::imports[]


class Search:

    @staticmethod
    def __call__(*args: str):
        cluster = Cluster.connect("localhost", ClusterOptions(PasswordAuthenticator("Administrator", "password")))
        bucket = cluster.bucket("travel-sample")
        collection = bucket.default_collection()

        """
== Examples

Search queries are executed at Cluster level (not bucket or collection).
Here is a simple MatchQuery that looks for the text “swanky” using a defined index:

[source,python]
----
include::example$search.py[tag=simple,indent=0]
----
"""
        # tag::simple[]
        import traceback
        try:
            result = cluster.search_query("index",
                                          QueryStringQuery("query"))
            for row in result.rows():
                print("Found row {}".format(row)
                print("Reported total rows: "
                      + result.metadata().metrics().total_rows())
        except CouchbaseException:
            logging.error(traceback.format_exc())
        # end::simple[]
        """
All simple query types are created in the same manner, some have additional properties, which can be seen in common query type descriptions.
    Couchbase FTS's xref:6.5@server:fts:fts-query-types.adoc[range of query types] enable powerful searching using multiple options, to ensure results are just within the range wanted.
Here is a date range query that looks for dates between 1st January 2019 and 31st January:

[source,python]
----
Exception in thread "main" com.couchbase.client.core.error.IndexNotFoundException: Index not found {"completed":true,"coreId":1,"httpStatus":400,"idempotent":true,"lastDispatchedFrom":"127.0.0.1:53818","lastDispatchedTo":"127.0.0.1:8094","requestId":3,"requestType":"SearchRequest","service":{"indexName":"unknown-index","type":"search"},"status":"INVALID_ARGS","timeoutMs":75000,"timings":{"dispatchMicros":18289,"totalMicros":1359398}}
----

[NOTE]
.Open Buckets and Cluster-Level Queries
====
If you are using a cluster older than Couchbase Server 6.5, it is required that there is at least one bucket open before performing a cluster-level query. 
If you fail to do so, the SDK will return a `FeatureNotAvailableException` with a descriptive error message asking you to open one.
====

== Search Queries

The second mandatory argument in the example above used `SearchQuery.queryString("query")` to specify the query to run against the search index. 
The query string is the simplest form, but there are many more available. 
The table below lists all of them with a short description of each. 
You can combine them with `conjuncts` and `disjuncts` respectively.

.Available Search Queries
[options="header"]
|====
| Name       | Description
| `QueryStringQuery(query)` | Accept query strings, which express query-requirements in a special syntax.
| `MatchQuery(String match)` | A match query analyzes input text, and uses the results to query an index.
| `MatchPhraseQuery(String matchPhrase)` | The input text is analyzed, and a phrase query is built with the terms resulting from the analysis.
| `PrefixQuery(String prefix)` | A prefix query finds documents containing terms that start with the specified prefix.
| `RegexQuery(String regexp)` | A regexp query finds documents containing terms that match the specified regular expression.
| `TermRangeQuery()` | A term range query finds documents containing a term in the specified field within the specified range.
| `NumericRangeQuery()` | A numeric range query finds documents containing a numeric value in the specified field within the specified range.
| `DateRangeQuery()` | A date range query finds documents containing a date value, in the specified field within the specified range.
| `DisjunctionQuery(SearchQuery... queries)` | A disjunction query contains multiple child queries. Its result documents must satisfy a configurable min number of child queries.
| `ConjunctionQuery(SearchQuery... queries)` | A conjunction query contains multiple child queries. Its result documents must satisfy all of the child queries.
| `WildcardQuery(String wildcard)` | A wildcard query uses a wildcard expression, to search within individual terms for matches.
| `DocIdQuery(String... docIds)` | A doc ID query returns the indexed document or documents among the specified set.
| `BooleanFieldQuery(bool value)` | A boolean field query searches fields that contain boolean true or false values.
| `TermQuery(String term)` | Performs an exact match in the index for the provided term.
| `PhraseQuery(String... terms)` | A phrase query searches for terms occurring in the specified position and offsets.
| `MatchAllQuery()` | Matches all documents in an index, irrespective of terms.
| `MatchNoneQuery()` | Matches no documents in the index.
| `GeoBoundingBoxQuery(double topLeftLon, double topLeftLat, double bottomRightLon, double bottomRightLat)` | Searches inside the given bounding box coordinates.
| `GeoDistanceQuery     (d          ouble locationLon, double locationLat, String distance)` | Searches inside the distance from the given location coordinate.
|====

== Search Options

The search service provides an array of options to customize your query. The following table lists them all:

.Available Search Options
[options="header"]
|====
| Name       | Description
| `limit(int)` | Allows to limit the number of hits returned.
| `skip(int)` | Allows to skip the first N hits of the results returned.
| `explain(bool)` | Adds additional explain debug information to the result.
| `scan_consistency(SearchScanConsistency)` | Specifies a different consistency level for the result hits.
| `consistent_with(MutationState)` | Allows to be consistent with previously performed mutations.
| `highlight(HighlightStyle, str...)` | Specifies highlighting rules for matched fields.
| `sort(Object)` | Allows to provide custom sorting rules.
| `facets(Map[str, SearchFacet])` | Allows to fetch facets in addition to the regular hits.
| `fields(str...)` | Specifies fields to be included.
| `serializer(JsonSerializer)` | Allows to use a different serializer for the decoding of the rows.
| `raw(str, Object)` | Escape hatch to add arguments that are not covered by these options.
|====

== The Search Result

Once the search query is executed successfully, the server starts sending back the resultant hits.

[source,python]
----
include::example$search.py[tag=squery,indent=0]
"""
        #tag::squery[]
        result = cluster.search_query("my-index-name", PrefixQuery("airports-"), SearchOptions(fields=["field-1"]))

        for row in result.rows():
            print("Score: {}".format(row.score()))
            print("Document Id: {}".format(row.id()))

            # Also print fields that are included in the query
            print(row.fields())
        #end::squery[]
        """
=== Limit and Skip

It is possible to limit the returned results to a maximum amount using the `limit` option.
    If you want to skip the first N records it can be done with the `skip` option.

[source,python]
"""

        #tag::limit[]
        result = cluster.search_query(
            "index",
            QueryStringQuery("query"),
            SearchOptions(skip=3, limit=4)
        )
        #end::limit[]
        """
----

=== ScanConsistency and ConsistentWith

By default, all search queries will return the data from whatever is in the index at the time of query.
These semantics can be tuned if needed so that the hits returned include the most recently performed mutations, at the cost of slightly higher latency since the index needs to be updated first.

There are two ways to control consistency: either by supplying a custom `SearchScanConsistency` or using `consistentWith`.
At the moment the cluster only supports `consistentWith`, which is why you only see `SearchScanConsistency.NOT_BOUNDED` in the enum which is the default setting.
The way to make sure that recently written documents show up in the rfc works as follows (commonly referred to "read your own writes" -- RYOW):

Like the Couchbase Query Service,
FTS allows `RequestPlus` queries -- _Read-Your-Own_Writes (RYOW)_ consistency, ensuring results contain information from updated indexes:

[source,python]
----
include::example$search.py[tag=ryow,indent=0]
"""
        #tag::ryow[]
        mutation_result = collection.upsert("key", {})
        mutation_state = MutationState().add_results(mutation_result)

        search_result = cluster.search_query(
            "index",
            QueryStringQuery("query"),
            SearchOptions().consistent_with(mutation_state))

        #end::ryow[]
        """
----

=== Highlight

It is possible to enable highlighting for matched fields.
You can either rely on the default highlighting style or provide a specific one.
The following snippet uses HTML formatting for two fields:

[source,python]
----
include::example$search.py[tag=highlight,indent=0]
----
"""
        #tag::highlight[]
        result = cluster.search_query(
            "index",
            QueryStringQuery("query"),
            SearchOptions(highlight_style=HighlightStyle.HTML, highlight_fields=["field1", "field2"]))

        #end::highlight[]
        """
=== Sort

By default the search engine will sort the results in descending order by score.
This behavior can be modified by providing a different sorting order which can also be nested.

[source,python]
----
include::example$search.py[tag=sort,indent=0]
----

"""
        #tag::sort[]
        result = cluster.search_query(
            "index",
            QueryStringQuery("query"),
            SearchOptions(sort=[SortScore(), SortField("field")]))
        #end::sort[]
        """
Facets are aggregate information collected on a result set and are useful when it comes to categorization of result data.
The SDK allows you to provide many different facet configurations to the search engine, the following example shows how to create a facet based on a term.
Other possible facets include numeric and date ranges.

=== Facets

[source,python]
----
include::example$search.py[tag=facets,indent=0]
----

"""
        # tag::facets[]

        result = cluster.search_query(
            "index",
            QueryStringQuery("query"),
            SearchOptions(facets=dict(categories=TermFacet("category", 5)))
        )
        # end::facets[]

        """
=== Fields

You can tell the search engine to include the full content of a certain number of indexed fields in the response.

                                                                                                        [source,java]
                                                                                                        ----
include::example$search.py[tag=fields,indent=0]
----
"""
        #tag::fields[]
        result = cluster.search_query(
            "index",
            QueryStringQuery("query"),
            SearchOptions(fields=["field1", "field2"])
          )
        #end::fields[]

# TODO: document async APIs?
# #tag::simplereactive[]
#   Mono<ReactiveSearchResult> result = cluster
#     .reactive()
#     .searchQuery("index", SearchQuery.queryString("query"));
#
#   result
#     .flatMapMany(ReactiveSearchResult::rows)
#     .subscribe(row -> System.out.println("Found row: " + row));
#   // #end::simplereactive[]
# }

        """
== Working with Results

The result of a search query has three components: hits, facets, and metdata.
    Hits are the documents that match the query.
    Facets allow the aggregation of information collected on a particular result set.
    Metdata holds additional information not directly related to your query,
                                                                      such as success total hits and how long the query took to execute in the cluster.

[source,python]
.Iterating hits
----
"""
        #tag::simpleresult[]
        for hit in result.hits():
            document_id = hit.id
            score = hit.score
        #end::simpleresult[]
        """
----

[source,python]
Iterating facets
               ----
"""
        #tag::simplefacetresult[]
        for facet in result.facets():
            name = facet.name
            total = facet.total
        #end::simplefacetresult[]
"""
----
The `SearchRow` contains the following methods:

.SearchRow
[options="header"]
|====
| `index()` | The name of the FTS index that gave this result.
                                                       | `id()` | The id of the matching document.
                                                                                         | `score()` | The score of this hit.
                                                                                                                         | `explanation()` | If enabled provides an explanation in JSON form.
                                                                                                                                                                                        | `locations()` | The individual locations of the hits as `SearchRowLocations`.
                                                                                                                                                                                                                                                  | `fragments()` | The fragments for each field that was requested as highlighted.
| `fieldsAs(final Class<T> target)` | Access to the returned fields, decoded via a `Class` type.
| `fieldsAs(final TypeRef<T> target)` | Access to the returned fields, decoded via a `TypeRef` type.
|====

Note that the `SearchMetaData` also contains potential `errors`, because the SDK will keep streaming results if the initial response came back successfully.
This makes sure that even with partial data usually search results are useable,
so if you absolutely need to check if all partitions are present in the result double check the error
(and not only catch an exception on the query itself).


=== Custom JSON Serializer

As with all JSON APIs, it is possible to customize the JSON serializer.
You can plug in your own library (like GSON) or custom configure mappings on your own Jackson serializer.
This in turn makes it possible to serialize rows into POJOs or other structures that your application defines, and which the SDK has no idea about.

Please see the documentation on transcoding and serialization for more information.

== Reactive And Async APIs

In addition to the blocking API on `Cluster`, the SDK provides reactive and async APIs on `ReactiveCluster` or `AsyncCluster` respectively.
If you are in doubt of which API to use, we recommend looking at the reactive first:
    it builds on top of reactor, a powerful library that allows you to compose reactive computations and deal with error handling and other related concerns (like retry) in an elegant manner.
The async API on the other hand exposes a `CompletableFuture` and is more meant for lower level integration into other libraries or if you need the last drop of performance.

There is another reason for using the reactive API here: streaming large results with backpressure from the application side.
Both the blocking and async APIs have no means of signalling backpressure in a good way, so if you need it the reactive API is your best option.

[TIP]
.Advanced Reactive Concepts Ahead
====
Please see recent guides to reactive programming for more information on the basics -- this guide dives straight into their impact on querying search.
====

A simple reactive query is similar to the blocking one:

    [source,java]
    ----
    include::example$search.py[tag=simplereactive,indent=0]
----

This search query will stream all rows as they become available form the server.
    If you want to manually control the data flow (which is important if you are streaming a lot of rows which could cause a potential out of memory situation) you can do this by using explicit `request()` calls.

                                                                                                                                                                                                              [source,java]
                                                                                                                                                                                                              ----
include::example$search.py[tag=backpressure,indent=0]
----

In this example we initially request a batch size of 10 rows (so streaming can begin).
Then as each row gets streamed it is written to a `process()` method which does whatever it needs to do to process.
    Then a counter is decremented, and once all of the 10 outstanding rows are processed another batch is loaded.
    Please note that with reactive code, if your `process()` method equivalent is blocking, you *must* move it onto another scheduler so that the I/O threads are not stalled.
We always recommend not blocking in the first place in reactive code.
"""
