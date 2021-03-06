"""
Mocks hurray server messages
"""

# TODO this does not work at the moment. Does it really make sense to mock the
# whole server, duplicating most of the server code?

from hurraypy.protocol import (CMD_CREATE_DATABASE, CMD_USE_DATABASE,
                               CMD_CREATE_GROUP, CMD_REQUIRE_GROUP,
                               CMD_CREATE_DATASET, CMD_GET_NODE, CMD_GET_KEYS,
                               CMD_GET_TREE,
                               CMD_SLICE_DATASET, CMD_BROADCAST_DATASET,
                               CMD_ATTRIBUTES_GET, CMD_ATTRIBUTES_SET,
                               CMD_ATTRIBUTES_CONTAINS, CMD_ATTRIBUTES_KEYS,
                               CMD_KW_CMD, CMD_KW_ARGS, CMD_KW_DB, CMD_KW_PATH,
                               CMD_KW_DATA, RESPONSE_NODE_TYPE, NODE_TYPE_GROUP,
                               NODE_TYPE_DATASET, RESPONSE_NODE_SHAPE,
                               RESPONSE_NODE_DTYPE, CMD_KW_KEY,
                               CMD_KW_STATUS, RESPONSE_ATTRS_CONTAINS,
                               RESPONSE_ATTRS_KEYS, RESPONSE_NODE_KEYS,
                               RESPONSE_NODE_TREE)

from hurraypy.status_codes import (FILE_EXISTS, OK, FILE_NOT_FOUND,
                                   GROUP_EXISTS, NODE_NOT_FOUND,
                                   DATASET_EXISTS, VALUE_ERROR, TYPE_ERROR,
                                   CREATED, UNKNOWN_COMMAND, MISSING_ARGUMENT,
                                   MISSING_DATA, KEY_ERROR, INVALID_ARGUMENT)

DATABASE_COMMANDS = (
    CMD_CREATE_DATABASE,
    CMD_USE_DATABASE
)

NODE_COMMANDS = (CMD_CREATE_GROUP,
                 CMD_CREATE_DATASET,
                 CMD_GET_NODE,
                 CMD_SLICE_DATASET,
                 CMD_BROADCAST_DATASET,
                 CMD_ATTRIBUTES_GET,
                 CMD_ATTRIBUTES_SET,
                 CMD_ATTRIBUTES_CONTAINS,
                 CMD_ATTRIBUTES_KEYS)


class Group():
    def __init__(self):
        self.attrs = {}


class Dataset():
    def __init__(self, data=None):
        self.attrs = {}
        self.data = data
        self.shape = data.shape
        self.dtype = data.dtype


class MockServer(object):
    def __init__(self):
        self.dbs = {}

    def response(self, status, data=None):
        resp = {
            CMD_KW_STATUS: status
        }
        if data is not None:
            resp["data"] = data

        # return resp
        return msgpack.packb(resp, default=encode_msgpack, use_bin_type=True)

    def db_exists(self, database):
        """
        Check if given database file exists
        :param database:
        :return:
        """
        return database in self.dbs.keys()

    def handle_request(self, msg):
        """
        Process hurray message
        :param msg: Message dictionary with 'cmd' and 'args' keys
        :return: Msgpacked response as bytes
        """
        cmd = msg.get(CMD_KW_CMD, None)
        args = msg.get(CMD_KW_ARGS, {})

        status = OK
        data = None

        if cmd in DATABASE_COMMANDS:  # Database related commands
            # Database name has to be defined
            if CMD_KW_DB not in args:
                return self.response(MISSING_ARGUMENT)
            db = args[CMD_KW_DB]
            if len(db) < 1:
                return self.response(INVALID_ARGUMENT)
            if cmd == CMD_CREATE_DATABASE:
                if self.db_exists(db):
                    status = FILE_EXISTS
                else:
                    self.dbs[db] = {}
                    status = CREATED
            elif cmd == CMD_USE_DATABASE:
                if not self.db_exists(db):
                    status = FILE_NOT_FOUND

        elif cmd in NODE_COMMANDS:  # Node related commands
            # Database name and path have to be defined
            if CMD_KW_DB not in args or CMD_KW_PATH not in args:
                return self.response(MISSING_ARGUMENT)

            db_name = args.get(CMD_KW_DB)
            # check if database exists
            if not self.db_exists(db_name):
                return self.response(FILE_NOT_FOUND)

            db = self.dbs[db_name]
            path = args[CMD_KW_PATH]

            if len(path) < 1:
                return self.response(INVALID_ARGUMENT)

            if cmd == CMD_CREATE_GROUP:
                if path in db:
                    status = GROUP_EXISTS
                else:
                    db[path] = Group()

            if cmd == CMD_REQUIRE_GROUP:
                db[path] = Group()

            elif cmd == CMD_CREATE_DATASET:
                if path in db:
                    status = DATASET_EXISTS
                else:
                    if CMD_KW_DATA not in msg:
                        return self.response(MISSING_DATA)
                    dst = Dataset(data=msg[CMD_KW_DATA])
                    db[path] = dst
                    data = dst

            else:  # Commands for existing nodes
                if path not in db:
                    return self.response(NODE_NOT_FOUND)

                if cmd == CMD_GET_NODE:
                    node = db[path]
                    # let the msgpack encoder handle encoding of
                    # Groups/Datasets
                    data = node
                elif cmd == CMD_GET_KEYS:
                    node = db[path]
                    if isinstance(node, Group):
                        data = {
                            # without list() it does not work with py3 (returns
                            # a view on a closed hdf5 file)
                            RESPONSE_NODE_KEYS: list(node.keys())
                        }
                    elif isinstance(node, Dataset):
                        return self.response(INVALID_ARGUMENT)
                elif cmd == CMD_GET_TREE:
                    node = db[path]
                    if isinstance(node, Group):
                        tree = node.tree()
                        data = {
                            RESPONSE_NODE_TREE: tree
                        }
                    elif isinstance(node, Dataset):
                        return self.response(INVALID_ARGUMENT)
                elif cmd == CMD_SLICE_DATASET:
                    if CMD_KW_KEY not in args:
                        return self.response(MISSING_ARGUMENT)
                    try:
                        data = db[path].data[args[CMD_KW_KEY]]
                    except ValueError:
                        status = VALUE_ERROR

                elif cmd == CMD_BROADCAST_DATASET:
                    if CMD_KW_DATA not in msg:
                        return self.response(MISSING_DATA)
                    if CMD_KW_KEY not in args:
                        return self.response(MISSING_ARGUMENT)
                    try:
                        db[path].data[args[CMD_KW_KEY]] = msg[CMD_KW_DATA]
                    except ValueError:
                        status = VALUE_ERROR
                    except IndexError:
                        status = TYPE_ERROR

                elif cmd == CMD_ATTRIBUTES_SET:
                    if CMD_KW_KEY not in args:
                        return self.response(MISSING_ARGUMENT)
                    key = args[CMD_KW_KEY]
                    if len(key) < 1:
                        return self.response(INVALID_ARGUMENT)
                    if CMD_KW_DATA in msg:
                        db[path].attrs[args[CMD_KW_KEY]] = msg[CMD_KW_DATA]
                    else:
                        return self.response(MISSING_DATA)
                elif cmd == CMD_ATTRIBUTES_GET:
                    if CMD_KW_KEY not in args:
                        return self.response(MISSING_ARGUMENT)
                    try:
                        data = db[path].attrs[args[CMD_KW_KEY]]
                    except KeyError:
                        status = KEY_ERROR

                elif cmd == CMD_ATTRIBUTES_CONTAINS:
                    if CMD_KW_KEY not in args:
                        return self.response(MISSING_ARGUMENT)
                    data = {RESPONSE_ATTRS_CONTAINS:
                            args[CMD_KW_KEY] in db[path].attrs}
                elif cmd == CMD_ATTRIBUTES_KEYS:
                    data = {RESPONSE_ATTRS_KEYS: db[path].attrs.keys()}
        else:
            status = UNKNOWN_COMMAND

        return self.response(status, data)

    def run(self, cmd, args, data=None):
        """
        Mocks all server calls
        :param cmd:
        :param args:
        :param data:
        :return:
        """

        return self.handle_request({
            CMD_KW_CMD: cmd,
            CMD_KW_ARGS: args,
            CMD_KW_DATA: data
        })
