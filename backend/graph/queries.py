"""Suggested Neo4j query templates for later graph integration.

These are intentionally parameterized and designed to be safe, readable, and easy
for future phases to adapt when Neo4j is available locally.
"""

FIND_WALLET_QUERY = """
MATCH (w:Wallet {wallet_id: $wallet_id})
OPTIONAL MATCH (w)--(t:Transaction)
OPTIONAL MATCH (w)<-[:ASSOCIATED_WITH]-(ip:IP)
RETURN w, collect(DISTINCT t) AS transactions, collect(DISTINCT ip) AS ips
"""

FIND_RELATED_TRANSACTIONS_QUERY = """
MATCH (w:Wallet {wallet_id: $wallet_id})<-[:INPUT_FROM|OUTPUT_TO]-(tx:Transaction)
RETURN DISTINCT tx
ORDER BY tx.timestamp DESC
"""

FIND_RELATED_IPS_QUERY = """
MATCH (w:Wallet {wallet_id: $wallet_id})<-[:ASSOCIATED_WITH]-(ip:IP)
RETURN DISTINCT ip
"""

FIND_CONNECTED_WALLETS_QUERY = """
MATCH (w:Wallet {wallet_id: $wallet_id})-[:INPUT_FROM|OUTPUT_TO]-(tx:Transaction)
MATCH (tx)-[:INPUT_FROM|OUTPUT_TO]-(other:Wallet)
WHERE other.wallet_id <> $wallet_id
RETURN DISTINCT other
"""

NEIGHBORHOOD_QUERY = """
MATCH path = (start:Wallet {wallet_id: $wallet_id})-[*1..3]-(neighbor)
RETURN path
LIMIT $limit
"""

CLEAR_GRAPH_QUERY = "MATCH (n) DETACH DELETE n"
