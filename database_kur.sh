#!/usr/bin/env bash
set -euo pipefail

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

step() {
  echo -e "${YELLOW}[${1}]${NC} ${2}"
}

success() {
  echo -e "${GREEN}${1}${NC}"
}

error() {
  echo -e "${RED}${1}${NC}" >&2
}

step "1/4" "Docker kontrolü"
if ! command -v docker >/dev/null 2>&1; then
  error "Docker bulunamadı. https://docs.docker.com/get-docker/ adresinden kurunuz."
  exit 1
fi
success "Docker bulundu: $(docker --version)"

step "2/4" ".env dosyası kontrolü"
ENV_FILE="backend/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cat <<'EOF' > "$ENV_FILE"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatcore
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
AI_PROVIDER=GEMINI
GEMINI_API_KEY=your-gemini-api-key-here
COMPANY_NAME=Company1
ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
EOF
  success ".env oluşturuldu (örnek değerlerle)."
else
  success ".env zaten mevcut, atlanıyor."
fi

step "3/4" "Docker servisleri (PostgreSQL & Redis) başlatılıyor"
docker compose up -d postgres redis || {
  error "Docker servisleri başlatılamadı. Docker Desktop çalışıyor mu? Port 5432 ve 6379 boş mu?"
  exit 1
}
success "Docker servisleri arka planda çalışıyor. 15 saniye bekleniyor..."
sleep 15

step "4/4" "Veritabanı migrasyonları"
cd backend
if [[ -f "../venv/bin/activate" ]]; then
  source ../venv/bin/activate
fi
alembic upgrade head || {
  error "Migrasyonlar başarısız oldu. 
  Manuel komut: cd backend && alembic upgrade head"
  exit 1
}
success "Migrasyonlar tamamlandı."

echo "Default kullanıcılar oluşturuluyor..."
python scripts/seed_users.py || {
  error "Kullanıcı oluşturulamadı. Manuel komut: python backend/scripts/seed_users.py"
}

success "Database kurulumu tamamlandı!"
cat <<'MSG'
Servisler:
- PostgreSQL: localhost:5432
- Redis:      localhost:6379

Varsayılan kullanıcılar:
- admin / 1234
- user2 / 1234
- user3 / 12345

Not: Backend'i yeniden başlatmayı unutmayın.
MSG
