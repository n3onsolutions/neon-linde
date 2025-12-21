FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose Vite development port
EXPOSE 5173

# Development command (overridden by docker-compose if needed)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
