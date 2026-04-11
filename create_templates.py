import os

def create_all_templates():
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    templates = {
        'staff.html': '''{% extends "base.html" %}

{% block title %}Staff Management{% endblock %}

{% block header %}Staff Management{% endblock %}

{% block actions %}
<div class="btn-group">
    <a href="{{ url_for('add_staff') }}" class="btn btn-success">
        <i class="bi bi-person-plus"></i> Add Staff
    </a>
</div>
{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Username</th>
                        <th>Full Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Department</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for staff_member in staff %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ staff_member.username }}</strong></td>
                        <td>{{ staff_member.full_name }}</td>
                        <td>{{ staff_member.email }}</td>
                        <td>
                            {% if staff_member.role == 'admin' %}
                            <span class="badge bg-danger">Admin</span>
                            {% elif staff_member.role == 'librarian' %}
                            <span class="badge bg-primary">Librarian</span>
                            {% elif staff_member.role == 'teacher' %}
                            <span class="badge bg-success">Teacher</span>
                            {% else %}
                            <span class="badge bg-secondary">{{ staff_member.role }}</span>
                            {% endif %}
                        </td>
                        <td>{{ staff_member.department or 'N/A' }}</td>
                        <td>
                            {% if staff_member.is_active %}
                            <span class="badge bg-success">Active</span>
                            {% else %}
                            <span class="badge bg-danger">Inactive</span>
                            {% endif %}
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                {% if staff_member.id != current_user.id %}
                                <form method="POST" action="{{ url_for('toggle_staff_status', staff_id=staff_member.id) }}" 
                                      onsubmit="return confirm('Are you sure?');" style="display: inline;">
                                    {% if staff_member.is_active %}
                                    <button type="submit" class="btn btn-outline-warning" title="Deactivate">
                                        <i class="bi bi-person-x"></i>
                                    </button>
                                    {% else %}
                                    <button type="submit" class="btn btn-outline-success" title="Activate">
                                        <i class="bi bi-person-check"></i>
                                    </button>
                                    {% endif %}
                                </form>
                                {% endif %}
                                {% if current_user.role == 'admin' and staff_member.id != current_user.id %}
                                <form method="POST" action="{{ url_for('delete_staff', staff_id=staff_member.id) }}" 
                                      onsubmit="return confirm('Are you sure you want to delete this staff member?');" style="display: inline;">
                                    <button type="submit" class="btn btn-outline-danger" title="Delete">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </form>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="8" class="text-center">No staff members found</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="card mt-3">
    <div class="card-header">
        <h5 class="mb-0">Role Descriptions</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-4">
                <div class="alert alert-danger">
                    <h6><i class="bi bi-shield-check"></i> Admin</h6>
                    <small>Full system access. Can manage staff, books, and all system settings.</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="alert alert-primary">
                    <h6><i class="bi bi-book"></i> Librarian</h6>
                    <small>Can manage books, handle borrowing/returns, and generate reports.</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="alert alert-success">
                    <h6><i class="bi bi-person"></i> Teacher</h6>
                    <small>Can borrow books and view their own borrowing history.</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
        
        # Add other templates here if needed
    }
    
    for template_name, template_content in templates.items():
        template_path = os.path.join(templates_dir, template_name)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"✓ Created: {template_path}")

if __name__ == "__main__":
    create_all_templates()
    print("\nAll templates created successfully!")
    print("Now run: python app.py")