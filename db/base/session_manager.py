import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..models import Base


def _ensure_sqlite_directory(db_path: str) -> None:
    """确保 SQLite 文件所在目录存在

    SQLite 连接时不会自动创建父目录，在容器/云平台首次启动、目录尚不存在
    （例如挂载的持久化卷还未初始化）时会直接报错。这里在建立连接前主动创建。
    """
    if not db_path.startswith('sqlite:///'):
        return
    raw_path = db_path[len('sqlite:///'):]
    if not raw_path or raw_path == ':memory:':
        return
    dir_name = os.path.dirname(raw_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)


class SessionManager:
    """
    数据库会话管理器

    职责：
    1. 管理数据库连接和会话
    2. 提供统一的会话上下文管理
    3. 处理事务和异常回滚
    """

    def __init__(self, db_path='sqlite:///data/tea_house.db'):
        """
        初始化会话管理器

        Args:
            db_path: 数据库连接路径
        """
        _ensure_sqlite_directory(db_path)
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    @contextmanager
    def session_scope(self):
        """
        提供会话上下文管理
        
        自动处理：
        - 会话创建和关闭
        - 事务提交和回滚
        - 异常处理
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        """关闭会话管理器"""
        self.Session.remove()
        self.engine.dispose()
