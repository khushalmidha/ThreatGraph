import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from alembic.migration import MigrationContext
from alembic.autogenerate import produce_migrations, render_python_code
from app.models import Base

engine = create_engine("sqlite:///:memory:", poolclass=NullPool)
conn = engine.connect()

context = MigrationContext.configure(
    conn, 
    opts={"compare_type": True, "compare_server_default": True}
)

migrations = produce_migrations(context, Base.metadata)

upgrade_code = render_python_code(migrations.upgrade_ops)
downgrade_code = render_python_code(migrations.downgrade_ops)

file_path = "alembic/versions/7d43401b57fb_initial.py"
with open(file_path, "r") as f:
    content = f.read()

new_content = content.replace("def upgrade() -> None:\n    pass", f"def upgrade() -> None:\n{upgrade_code}")
new_content = new_content.replace("def downgrade() -> None:\n    pass", f"def downgrade() -> None:\n{downgrade_code}")
new_content = "from sqlalchemy.dialects import postgresql\n" + new_content

with open(file_path, "w") as f:
    f.write(new_content)

print("Migration file written successfully")
