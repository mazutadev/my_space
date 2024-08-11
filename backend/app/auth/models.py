from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import logger, db


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
    def _check_role_instance(cls, identifier):
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
    def create(cls, name, description=None):
        role_instance = cls.query.filter_by(name=name).first()
        if role_instance:
            logger.info(f'Role with name {name} already exist. Return exist role instance') # Replace on logging
            return role_instance

        role = cls(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        return role
    

    @classmethod
    def delete(cls, identifier, new_role_identifier=None):
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
    def update(cls, identifier, new_name=None, new_description=None):
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
    def read(cls, identifier):
        return cls._check_role_instance(identifier)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.S)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)