# Copyright (c) 2016, Meteotest
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of Meteotest nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# 1xx: Success
OK = 100
CREATED = 101
UPDATED = 102

# 2xx: Message error
UNKNOWN_COMMAND = 200
MISSING_ARGUMENT = 201
INVALID_ARGUMENT = 202
MISSING_DATA = 203
INCOMPATIBLE_DATA = 204  # incompatible shape and/or dtype

# 3xx: Database Error
FILE_EXISTS = 300
FILE_NOT_FOUND = 301

# 4xx: Node Error
GROUP_EXISTS = 400
DATASET_EXISTS = 401
NODE_NOT_FOUND = 402
VALUE_ERROR = 403
TYPE_ERROR = 404
KEY_ERROR = 405

# 5xx: Server Error
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501


# translate status code to human readable text
STATUS_MSGS = {
    OK: "OK",
    CREATED: "resource successfully created",
    UPDATED: "resource successfully updated",

    UNKNOWN_COMMAND: "unknown command",
    MISSING_ARGUMENT: "missing argument",
    INVALID_ARGUMENT: "invalid argument",
    MISSING_DATA: "missing data",
    INCOMPATIBLE_DATA: "incompatible dtype and/or shape ",

    FILE_EXISTS: "file already exists",
    FILE_NOT_FOUND: "file not found",

    GROUP_EXISTS: "group already exists",
    DATASET_EXISTS: "dataset already exists",
    NODE_NOT_FOUND: "node not found",
    VALUE_ERROR: "illegal argument",
    TYPE_ERROR: "invalid argument or slicing object",
    KEY_ERROR: "key error",

    INTERNAL_SERVER_ERROR: "internal server error",
    NOT_IMPLEMENTED: "not implemented",
}


def get_msg(status):
    return STATUS_MSGS.get(status, str(status))
