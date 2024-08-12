from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import logger, db


@contextmanager
def transaction_scope():
    try:
        yield
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f'Transaction failed: {e}')
        raise


user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


    def __repr__(self):
        return f"<Role(name='{self.name}', description='{self.description}')>"
    

    @classmethod
    def _check_role_instance(cls, identifier) -> 'Role':
        role_instance = None
        if isinstance(identifier, int):
            role_instance = cls.query.get(identifier)
        elif isinstance(identifier, str):
            role_instance = cls.query.filter_by(name=identifier).first()
        if not role_instance:
            logger.error(f'Role with identifier {identifier} does not exist')
            raise ValueError(f'Role with identifier {identifier} does not exist')
        return role_instance
    

    @classmethod
    def create(cls, name: str, description: str = None) -> 'Role':
        role_instance = cls.query.filter_by(name=name).first()
        if role_instance:
            logger.info(f'Role with name {name} already exist. Return exist role instance') # Replace on logging
            return role_instance

        role = cls(name=name, description=description)

        try:
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            logger.error(f'Failed to create role {name}: {e}')
            db.session.rollback()
            raise

        return role
    

    @classmethod
    def delete(cls, identifier, new_role_identifier: str = None) -> 'Role':
        role_instance = cls._check_role_instance(identifier)

        if new_role_identifier:
            new_role = cls._check_role_instance(new_role_identifier)
            for user in role_instance.users:
                user.roles.remove(role_instance)
                user.add_role(new_role)
            logger.info(f'Role {role_instance.name} has been reassigned to {new_role.name} for all users.')
        else:
            for user in role_instance.users:
                user.roles.remove(role_instance)
            logger.info(f'Role {role_instance.name} has been removed from all users.')

        db.session.delete(role_instance)
        db.session.commit()
        return role_instance
    

    @classmethod
    def update(cls, identifier, new_name:str = None, new_description: str = None) -> 'Role':
        role_instance = cls._check_role_instance(identifier)
        if new_name:
            check_exist_role = cls.query.filter_by(name=new_name).first()
            if check_exist_role:
                raise ValueError(f'Role with name {new_name} already exist')
            role_instance.name = new_name
            logger.info(f'Role Id/Name {identifier} name updated to {new_name}')
        if new_description:
            role_instance.description = new_description
            logger.info(f'Role ID {identifier} description updated.')
        db.session.commit()
        return role_instance
    

    @classmethod
    def read(cls, identifier) -> 'Role':
        return cls._check_role_instance(identifier)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    roles = db.relationship('Role', 
                            secondary=user_roles, 
                            lazy='subquery', 
                            backref=db.backref('users', lazy=True))


    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


    def set_password(self, password: str):
        self.password = generate_password_hash(password)
        logger.info(f'Password set for user {self.username}')


    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
    

    def _validate_role_object(self, role: 'Role'):
        if not isinstance(role, Role):
            logger.error(f'Expected Role object, got {type(role).__name__} instead')
            raise TypeError(f'Expected Role object, got {type(role).__name__} instead')
    

    def add_role(self, role: 'Role', commit: bool = True):
        self._validate_role_object(role)

        if role not in self.roles:
            self.roles.append(role)
            logger.info(f'Role {role.name} added to user {self.username}')
            if commit:
                try:
                    db.session.commit()
                except SQLAlchemyError as e:
                    logger.error(f'Failed to commit role change for user {self.username}: {e}')
                    db.session.rollback()
                    raise
        else:
            logger.error(f'Role {role.name} already exists in user {self.username} roles')
            raise ValueError(f'Role {role.name} already exists in user {self.username} roles')


    def remove_role(self, role: 'Role', commit: bool = True):
        self._validate_role_object(role)
        if role in self.roles:
            self.roles.remove(role)
            logger.info(f'Role {role.name} removed from user {self.username}')
            if commit:
                try:
                    db.session.commit()
                except SQLAlchemyError as e:
                    logger.error(f'Failed to commit role change for user {self.username}: {e}')
                    db.session.rollback()
                    raise
        else:
            logger.error(f'Role {role.name} does not exist in user {self.username} roles')
            raise ValueError(f'Role {role.name} does not exist in user {self.username} roles')
        
    
    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
    

    @classmethod
    def create(cls, username: str, email: str, password: str, roles: list['Role'] = None) -> 'User':
        def assign_roles_to_user(user, roles):
            with transaction_scope():
                for role in roles:
                    user.add_role(role, commit=False)

        existing_username = cls.query.filter_by(username=username).first()
        existing_email = cls.query.filter_by(email=email).first()

        if existing_username:
            logger.warning(f'User with username {username} already exists.')
            raise ValueError(f'User with username {username} already exists.')
        if existing_email:
            logger.warning(f'User with email {email} already exists.')
            raise ValueError(f'User with email {email} already exists.')
        
        new_user = cls(username=username, email=email)
        new_user.set_password(password)

        if roles:
            assign_roles_to_user(new_user, roles)

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            logger.error(f'Failed to create user {username}: {e}')
            db.session.rollback()
            raise

        return new_user
