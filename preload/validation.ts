// Comprehensive input validation for IPC security

function validateString(input, fieldName, maxLength = 1000) {
  if (!input || typeof input !== 'string') {
    throw new Error(`Invalid ${fieldName}: must be a non-empty string`);
  }
  if (input.length > maxLength) {
    throw new Error(`Invalid ${fieldName}: exceeds maximum length of ${maxLength}`);
  }
  
  // Remove potential XSS/injection attempts
  const sanitized = input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/data:(?!image\/)/gi, ''); // Allow only image data URLs
  
  return sanitized;
}

function validateId(input, fieldName) {
  if (!input || typeof input !== 'string') {
    throw new Error(`Invalid ${fieldName}: must be a string`);
  }
  
  // Allow only alphanumeric, hyphens, underscores, and dots
  if (!/^[a-zA-Z0-9._-]+$/.test(input)) {
    throw new Error(`Invalid ${fieldName}: contains invalid characters`);
  }
  
  if (input.length > 100) {
    throw new Error(`Invalid ${fieldName}: too long`);
  }
  
  return input;
}

function validateObject(input, fieldName, maxKeys = 50) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throw new Error(`Invalid ${fieldName}: must be an object`);
  }
  
  if (Object.keys(input).length > maxKeys) {
    throw new Error(`Invalid ${fieldName}: too many properties`);
  }
  
  // Deep validation to prevent prototype pollution
  const sanitized = {};
  for (const [key, value] of Object.entries(input)) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue; // Skip dangerous keys
    }
    
    if (typeof value === 'string') {
      sanitized[key] = validateString(value, `${fieldName}.${key}`, 10000);
    } else if (typeof value === 'number' && Number.isFinite(value)) {
      sanitized[key] = value;
    } else if (typeof value === 'boolean') {
      sanitized[key] = value;
    } else if (Array.isArray(value)) {
      sanitized[key] = validateArray(value, `${fieldName}.${key}`, 100);
    } else if (value === null || value === undefined) {
      sanitized[key] = value;
    } else if (typeof value === 'object') {
      sanitized[key] = validateObject(value, `${fieldName}.${key}`, 20);
    }
    // Skip functions and other types
  }
  
  return sanitized;
}

function validateArray(input, fieldName, maxLength = 100) {
  if (!Array.isArray(input)) {
    throw new Error(`Invalid ${fieldName}: must be an array`);
  }
  
  if (input.length > maxLength) {
    throw new Error(`Invalid ${fieldName}: too many items`);
  }
  
  // Validate array contents
  return input.map((item, index) => {
    if (typeof item === 'string') {
      return validateString(item, `${fieldName}[${index}]`, 1000);
    } else if (typeof item === 'number' && Number.isFinite(item)) {
      return item;
    } else if (typeof item === 'boolean') {
      return item;
    } else if (typeof item === 'object' && item !== null) {
      return validateObject(item, `${fieldName}[${index}]`, 20);
    } else if (item === null || item === undefined) {
      return item;
    } else {
      throw new Error(`Invalid ${fieldName}[${index}]: unsupported type`);
    }
  });
}

function validateUrl(input, fieldName) {
  const urlString = validateString(input, fieldName, 2000);
  
  try {
    const url = new URL(urlString);
    
    // Whitelist allowed protocols
    const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
    if (!allowedProtocols.includes(url.protocol)) {
      throw new Error(`Invalid ${fieldName}: protocol not allowed`);
    }
    
    // Block localhost in production unless explicitly allowed
    if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') {
      const isDevMode = process.env.NODE_ENV === 'development';
      if (!isDevMode) {
        throw new Error(`Invalid ${fieldName}: localhost not allowed in production`);
      }
    }
    
    return urlString;
  } catch (error) {
    throw new Error(`Invalid ${fieldName}: ${error.message}`);
  }
}

function validatePath(input, fieldName) {
  const pathString = validateString(input, fieldName, 500);
  
  // Remove any path traversal attempts
  const normalized = pathString
    .replace(/\.\./g, '')
    .replace(/\/+/g, '/')
    .replace(/^\//, '');
  
  // Additional security: no absolute paths
  if (pathString.startsWith('/') || pathString.includes(':')) {
    throw new Error(`Invalid ${fieldName}: absolute paths not allowed`);
  }
  
  return normalized;
}

// Rate limiting for API calls
const rateLimits = new Map();

function checkRateLimit(operation, maxCalls = 60, windowMs = 60000) {
  const now = Date.now();
  const key = operation;
  
  if (!rateLimits.has(key)) {
    rateLimits.set(key, []);
  }
  
  const calls = rateLimits.get(key);
  
  // Remove old calls outside the window
  while (calls.length > 0 && now - calls[0] > windowMs) {
    calls.shift();
  }
  
  if (calls.length >= maxCalls) {
    throw new Error(`Rate limit exceeded for ${operation}`);
  }
  
  calls.push(now);
  return true;
}

module.exports = {
  validateString,
  validateId,
  validateObject,
  validateArray,
  validateUrl,
  validatePath,
  checkRateLimit
};