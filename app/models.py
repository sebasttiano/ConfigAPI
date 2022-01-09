# -*- coding: utf-8 -*-
"""ORM representation of the tables in DB"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()


class Tasks(Base):  # pylint: disable=too-few-public-methods
    """ Class for table tasks """

    __tablename__ = "tasks"
    __table_args__ = {
        "comment": "Tasks for execution and its statuses",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_general_ci"
    }

    task_id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True
    )
    status = Column(Enum("new", "success", "error"), server_default="new",
                    comment="Short description of the task status")
    device_id = Column(Integer, ForeignKey("devices.id"), comment="Ref to the device id")
    command = Column(String(128), comment="Command to execute")
    created_at = Column(DateTime, comment="Task creation time", server_default=func.now())
    last_changed = Column(DateTime, comment="The time of the last change in the status of the task")
    msg = Column(Text, comment="Status message")
    device = relationship("Devices", backref="devices", foreign_keys=[device_id])


class Devices(Base):  # pylint: disable=too-few-public-methods
    """ Class for table devices """

    __tablename__ = "devices"
    __table_args__ = {
        "comment": "List of network devices",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_general_ci"
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    name = Column(String(128), comment="Name of the device")
    type = Column(Enum("router", "switch"), comment="Network type")
    role = Column(Enum("asbr", "aggregation", "access", "spine", "leaf"),
                  comment="What is device used for")
    vendor = Column(Enum("juniper", "cisco"), comment="Vendor of the device")
    model = Column(String(128), comment="Model of the device")
    ip = Column(String(128), unique=True, comment="Ip address of the device")
    location = Column(String(128), comment="Location: DC-ROW-RACK")
    description = Column(Text, comment="Some additional description of the device, if necessary")
