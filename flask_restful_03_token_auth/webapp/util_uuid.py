from sqlalchemy.types import TypeDecorator
import uuid
import datetime


class UUIDOPS(TypeDecorator):
    def __init__(self, **kwargs):
        super(UUIDOPS, self).__init__(**kwargs)

    @classmethod
    def getNewUUIDhex(cls, length):
        """
        return Example
        if length=12:  d7279d485d19
        if not hex:    52fa4ec74e6b55c68fae6cde2737811a
        """

        if length:
            _uuid = str(uuid.uuid4().hex[:length] )
        else:
            _uuid = str(uuid.uuid4().hex )

        return _uuid

    @classmethod
    def getNewUUIDint(cls):
        """
        return Example
        154361650359658165359025540175530522867
        """
        now = str(datetime.datetime.now())
        return uuid.uuid5(uuid.NAMESPACE_DNS, now).int

    @classmethod
    def getNewUUIDStandard(cls):
        """
        return Example
        53ab65dd-7f5d-5236-89cd-502fd7a5b899
        """
        now = str(datetime.datetime.now())
        _uuid = uuid.uuid4
        return _uuid
