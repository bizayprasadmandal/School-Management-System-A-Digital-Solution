#!/bin/bash
# Integration walk-through: hits key endpoints of the modules fixed this session.
set -u
# Smoke test — hit the key module endpoints and verify list/create/duplicate flows.
# Credentials come from the environment (defaults match the local demo seed).
BASE="${API_BASE:-http://localhost:8000/api/v1}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@demo.edusphere.school}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-IntegrationPass1!}"
TOKEN=$(curl -s -X POST "$BASE/auth/login/" -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" \
  | python -c "import sys,json;print(json.load(sys.stdin)['access'])")
AUTH="Authorization: Bearer $TOKEN"

pass=0; fail=0
check() { # name expected_code method url [json_body]
  local name="$1" want="$2" method="$3" url="$4" body="${5:-}"
  local code
  if [ -n "$body" ]; then
    code=$(curl -s -o /tmp/intg_body.json -w "%{http_code}" -X "$method" "$url" -H "$AUTH" -H "Content-Type: application/json" -d "$body")
  else
    code=$(curl -s -o /tmp/intg_body.json -w "%{http_code}" -X "$method" "$url" -H "$AUTH")
  fi
  if [ "$code" = "$want" ]; then
    echo "OK   $name ($code)"; pass=$((pass+1))
  else
    echo "FAIL $name (got $code want $want): $(head -c 120 /tmp/intg_body.json)"; fail=$((fail+1))
  fi
}

INTAKE_ID=$(curl -s "$BASE/admissions/intakes/" -H "$AUTH" | python -c "import sys,json; d=json.load(sys.stdin); print(d['results'][0]['id'] if d.get('results') else '')")

# --- GETs (list views) ---
check "fees categories list"    200 GET "$BASE/fees/categories/"
check "fees structures list"    200 GET "$BASE/fees/structures/"
check "fees invoices list"      200 GET "$BASE/fees/invoices/"
check "fees payments list"      200 GET "$BASE/fees/payments/"
check "fees scholarships list"  200 GET "$BASE/fees/scholarships/"
check "admissions intakes"      200 GET "$BASE/admissions/intakes/"
check "admissions applications" 200 GET "$BASE/admissions/applications/"
check "admissions reviews"      200 GET "$BASE/admissions/reviews/"
check "cafeteria menus"         200 GET "$BASE/cafeteria/menus/"
check "cafeteria plans"         200 GET "$BASE/cafeteria/plans/"
check "cafeteria bookings"      200 GET "$BASE/cafeteria/bookings/"
check "library books"           200 GET "$BASE/library/books/"
check "library checkouts"       200 GET "$BASE/library/checkouts/"
check "transportation vehicles" 200 GET "$BASE/transport/vehicles/"
check "transportation drivers"  200 GET "$BASE/transport/drivers/"
check "transportation routes"   200 GET "$BASE/transport/routes/"
check "inventory categories"    200 GET "$BASE/inventory/categories/"
check "inventory suppliers"     200 GET "$BASE/inventory/suppliers/"
check "communication announcements" 200 GET "$BASE/communication/announcements/"
check "communication messages"  200 GET "$BASE/communication/messages/"

# --- POSTs (creates — the family that was 400ing) ---
UNIQ=$RANDOM$RANDOM
check "fees create category"   201 POST "$BASE/fees/categories/" "{\"name\":\"Integration Bus $UNIQ\",\"recurrence\":\"monthly\"}"
check "cafeteria create menu"  201 POST "$BASE/cafeteria/menus/" "{\"name\":\"Integration Lunch\",\"meal_type\":\"lunch\",\"date\":\"2026-11-${UNIQ:0:2}\",\"price\":\"4.50\"}"
check "library create book"    201 POST "$BASE/library/books/" "{\"title\":\"Integration Testing $UNIQ\",\"author\":\"QA Team\",\"isbn\":\"978-0-INT-$UNIQ\",\"total_copies\":3}"
check "transportation vehicle" 201 POST "$BASE/transport/vehicles/" "{\"plate_number\":\"INT-$UNIQ\",\"vehicle_type\":\"bus\",\"model_name\":\"Toyota Coaster\",\"capacity\":30,\"status\":\"active\"}"
check "inventory category"     201 POST "$BASE/inventory/categories/" "{\"name\":\"Walkthrough Supplies $UNIQ\"}"
check "announcement create"    201 POST "$BASE/communication/announcements/" "{\"title\":\"Integration Test $UNIQ\",\"content\":\"All systems operational.\",\"priority\":\"normal\",\"audience\":\"all\"}"
check "admissions application" 201 POST "$BASE/admissions/applications/" "{\"intake\":\"$INTAKE_ID\",\"first_name\":\"Walk\",\"last_name\":\"Through$UNIQ\",\"date_of_birth\":\"2012-01-01\",\"gender\":\"female\",\"email\":\"walkthrough${UNIQ}@example.com\",\"phone\":\"+1\",\"applying_for_grade\":\"5\"}"

# --- Duplicates must be clean 400s, not 500s ---
check "dup inventory category" 400 POST "$BASE/inventory/categories/" "{\"name\":\"Walkthrough Supplies $UNIQ\"}"
check "dup cafeteria menu"     400 POST "$BASE/cafeteria/menus/" "{\"name\":\"Integration Lunch dup\",\"meal_type\":\"lunch\",\"date\":\"2026-11-${UNIQ:0:2}\",\"price\":\"4.50\"}"
check "dup vehicle plate"      400 POST "$BASE/transport/vehicles/" "{\"plate_number\":\"INT-$UNIQ\",\"vehicle_type\":\"bus\",\"model_name\":\"Toyota Coaster\",\"capacity\":30,\"status\":\"active\"}"

echo ""
echo "PASS=$pass FAIL=$fail"
