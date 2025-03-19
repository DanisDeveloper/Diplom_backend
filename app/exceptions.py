from fastapi import HTTPException, status

UserAlreadyExistsException = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

UserNotAuthenticatedException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

InvalidPasswordException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

UserNotExistsException = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User not exists")

InvalidTokenException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

TokenExpiredException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

ForbiddenException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

UserIdNotFoundException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user id not found")

UserNotFoundException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

RefreshTokenNotFound = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")

InvalidRefreshTokenException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate refresh token")
