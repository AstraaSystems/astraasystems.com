#!/bin/bash
BASE="http://localhost:8000"
EMAIL="YOUR_TEST_EMAIL"
PASSKEY="YOUR_TEST_PASSKEY"

echo "== Login =="
TOKEN=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"passkey\":\"$PASSKEY\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin).get('token',''))")
echo "token: ${TOKEN:0:12}..."

AUTH="-H Authorization:Bearer=$TOKEN"

echo "== Add item =="
ADD=$(curl -s -X POST "$BASE/api/logistics/add" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"2x4 Lumber","sku":"LMB-24","category":"Framing","unit":"each","unit_cost":6.50,"quantity":40,"location":"Yard A","reorder_point":20,"supplier":"BC Building Supply","notes":"8ft SPF"}')
echo "$ADD"
ID=$(echo "$ADD" | python3 -c "import sys,json;print(json.load(sys.stdin).get('item',{}).get('id',''))")
echo "new id: $ID"

echo "== List =="
curl -s "$BASE/api/logistics/list" -H "Authorization: Bearer $TOKEN"
echo

echo "== Adjust -15 =="
curl -s -X POST "$BASE/api/logistics/adjust" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"id\":\"$ID\",\"delta\":-15}"
echo

echo "== Delete =="
curl -s -X POST "$BASE/api/logistics/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"id\":\"$ID\"}"
echo
echo "== Final list =="
curl -s "$BASE/api/logistics/list" -H "Authorization: Bearer $TOKEN"
echo
