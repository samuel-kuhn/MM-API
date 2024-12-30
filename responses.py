def clientError(error: str):
    """Returns a client error tuple."""
    return ({"error": error}, 400)

UnexpectedError = ({"error": "Unexpected error occured."}, 500)

Success = ({"status": "Success."}, 200)

UserMissing = clientError("Username missing.")

ServerNameMissing = clientError("Server name missing.")

ServerNotFound = clientError("Server not found.")


