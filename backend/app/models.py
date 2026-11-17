from sqlalchemy import (Column, Integer, String, Text, Boolean, Date, DateTime,
                        ForeignKey, UniqueConstraint, CheckConstraint, Index, func)
from sqlalchemy.orm import relationship
from .database import Base


BLOOD_GROUPS = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")
BG_LIST = ", ".join(f"'{g}'" for g in BLOOD_GROUPS)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # donor | hospital | admin
    is_approved = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    donor = relationship("Donor", back_populates="user", uselist=False)
    hospital = relationship("Hospital", back_populates="user", uselist=False)

    __table_args__ = (
        CheckConstraint("role IN ('donor','hospital','admin')", name="ck_users_role"),
    )


class Donor(Base):
    __tablename__ = "donors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     unique=True, nullable=False)
    blood_group = Column(String(3), nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    last_donation_date = Column(Date, nullable=True)
    is_available = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="donor")

    __table_args__ = (
        CheckConstraint(f"blood_group IN ({BG_LIST})", name="ck_donors_blood_group"),
        Index("ix_donors_match", "blood_group", "city", "is_available"),
    )


class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     unique=True, nullable=False)
    hospital_name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    license_no = Column(String(100), nullable=False)

    user = relationship("User", back_populates="hospital")


class BloodRequest(Base):
    __tablename__ = "blood_requests"
    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"),
                         nullable=False)
    blood_group = Column(String(3), nullable=False)
    units_needed = Column(Integer, nullable=False)
    units_fulfilled = Column(Integer, nullable=False, default=0)
    city = Column(String(100), nullable=False)
    urgency = Column(String(10), nullable=False, default="Normal")
    required_by = Column(DateTime(timezone=True), nullable=False)
    exact_match_only = Column(Boolean, nullable=False, default=False)
    note = Column(Text, nullable=True)
    status = Column(String(15), nullable=False, default="Open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(f"blood_group IN ({BG_LIST})", name="ck_requests_blood_group"),
        CheckConstraint("urgency IN ('Normal','Urgent','Critical')", name="ck_requests_urgency"),
        CheckConstraint("status IN ('Open','Fulfilled','Expired','Cancelled')", name="ck_requests_status"),
        Index("ix_requests_status_required_by", "status", "required_by"),
    )


class RequestResponse(Base):
    __tablename__ = "request_responses"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id", ondelete="CASCADE"),
                        nullable=False)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"),
                      nullable=False)
    status = Column(String(15), nullable=False, default="Notified")
    notified_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("request_id", "donor_id", name="uq_response_request_donor"),
        CheckConstraint("status IN ('Notified','Accepted','Declined','Donated')",
                        name="ck_responses_status"),
    )