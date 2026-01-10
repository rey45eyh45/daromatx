#!/bin/bash
# DAROMATX Bot - Deploy Script
# Usage: ./deploy.sh [command]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   DAROMATX Bot - Deploy Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Copy .env.example to .env and fill in the values"
    exit 1
fi

# Load environment variables
source .env

case "$1" in
    build)
        echo -e "${YELLOW}Building Docker images...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}Build completed!${NC}"
        ;;
    
    start)
        echo -e "${YELLOW}Starting services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}Services started!${NC}"
        docker-compose ps
        ;;
    
    stop)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}Services stopped!${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting services...${NC}"
        docker-compose restart
        echo -e "${GREEN}Services restarted!${NC}"
        ;;
    
    logs)
        if [ -z "$2" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f "$2"
        fi
        ;;
    
    status)
        docker-compose ps
        ;;
    
    ssl)
        echo -e "${YELLOW}Setting up SSL certificate...${NC}"
        if [ -z "$DOMAIN" ]; then
            echo -e "${RED}Error: DOMAIN not set in .env${NC}"
            exit 1
        fi
        
        # Initial certificate
        docker-compose run --rm certbot certonly \
            --webroot \
            --webroot-path=/var/www/certbot \
            --email $EMAIL \
            --agree-tos \
            --no-eff-email \
            -d $DOMAIN
        
        echo -e "${GREEN}SSL certificate obtained!${NC}"
        docker-compose restart nginx
        ;;
    
    update)
        echo -e "${YELLOW}Updating application...${NC}"
        git pull
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "${GREEN}Update completed!${NC}"
        ;;
    
    backup)
        echo -e "${YELLOW}Creating database backup...${NC}"
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose exec -T postgres pg_dump -U $DB_USER $DB_NAME > "./backups/$BACKUP_FILE"
        echo -e "${GREEN}Backup saved to backups/$BACKUP_FILE${NC}"
        ;;
    
    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: ./deploy.sh restore <backup_file>${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Restoring database from $2...${NC}"
        docker-compose exec -T postgres psql -U $DB_USER $DB_NAME < "$2"
        echo -e "${GREEN}Restore completed!${NC}"
        ;;
    
    *)
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build    - Build Docker images"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - View logs (optional: service name)"
        echo "  status   - Show service status"
        echo "  ssl      - Setup SSL certificate"
        echo "  update   - Update and restart"
        echo "  backup   - Backup database"
        echo "  restore  - Restore database from backup"
        ;;
esac
