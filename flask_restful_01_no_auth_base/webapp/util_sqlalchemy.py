from webapp.extensions import db

class SQLALCHEMYOPS:
    def __init__(self, **kwargs):
        super(APPOPS, self).__init__(**kwargs)

    @classmethod
    def to_jsonify(cls, res):
        l = []
        if isinstance(res, list) or cls.getClassName(res) == 'BaseQuery':
            for i in res:
                if cls.getClassName(i) == "Row" or cls.getClassName(i)== "result":
                    _d = {}
                    for x in i:
                        data = cls.row2dict(x)
                        tableName = str(cls.getTableName(x))
                        _d[tableName] = data
                    l.append(_d)
                elif '__main__' in str(type(i)):
                    data = cls.row2dict(i)
                    l.append(data)
                else:
                    data = cls.row2dict(i)
                    l.append(data)
        else:
            data = cls.row2dict(res)
            l.append(data)

        return l


    @staticmethod
    def getTableName(c):
        try:
            return c.__table__
        except:
            return 'tableNotFound'


    @staticmethod
    def row2dict(row):
        d = {}
        for column in row.__table__.columns:
            if column.name == "is_active":
                v = getattr(row, column.name)
                continue
            d[column.name] = getattr(row, column.name)

        return d

    # @staticmethod
    # def row3dict(row):
    #     d = row.__dict__
    #     d.pop('_sa_instance_state', None)
    #     # print("=== from row3dict", d)
    #     return d
    
    @staticmethod
    def getClassName(c):
        try:
            return type(c).__name__
        except:
            return ''
