from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import JsonResponse
from datetime import date
from calendar import monthrange
import json

from .models import (
    CustomUser, Project, ProjectMembership, VideoTitle,
    Log, LogVideoTitleAction, PhotoLogProgress
)
from .forms import (
    LoginForm, CustomPasswordChangeForm, NewEmployeeForm,
    CreateProjectForm, NewLogForm
)


def boss_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_boss:
            messages.error(request, "Ehhez boss jogosultság szükséges.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")
    return render(request, "tracking/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def home_view(request):
    user = request.user
    today = timezone.now().date()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    chart_data = _monthly_revenue(year, month) if user.is_boss else _user_daily_hours(user, year, month)
    return render(request, "tracking/home.html", {
        "chart_data": json.dumps(chart_data),
        "month": month, "year": year, "month_name": _month_name(month),
        "prev_month": prev_month, "prev_year": prev_year,
        "next_month": next_month, "next_year": next_year,
    })


@login_required
def password_change_view(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        update_session_auth_hash(request, form.save())
        messages.success(request, "Jelszó sikeresen megváltoztatva.")
        return redirect("home")
    return render(request, "tracking/password_change.html", {"form": form})


@boss_required
def boss_dashboard_view(request):
    today = timezone.now().date()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    return render(request, "tracking/boss_dashboard.html", {
        "chart_data": json.dumps(_monthly_revenue(year, month)),
        "month": month, "year": year, "month_name": _month_name(month),
        "prev_month": prev_month, "prev_year": prev_year,
        "next_month": next_month, "next_year": next_year,
    })


@boss_required
def employees_list_view(request):
    query = request.GET.get("q", "")
    qs = CustomUser.objects.filter(is_active=True)
    if query:
        qs = qs.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(username__icontains=query))
    today = timezone.now().date()
    data = []
    for emp in qs:
        mh = emp.logs.filter(date__month=today.month, date__year=today.year).aggregate(t=Sum("hours"))["t"] or 0
        data.append({"employee": emp, "monthly_hours": mh, "monthly_revenue": _emp_revenue(emp, today.month, today.year)})
    return render(request, "tracking/employees_list.html", {"employee_data": data, "query": query})


@boss_required
def employee_detail_view(request, employee_id):
    employee = get_object_or_404(CustomUser, pk=employee_id)
    project_data = []
    for m in ProjectMembership.objects.filter(user=employee).select_related("project"):
        proj = m.project
        hours = proj.logs.filter(user=employee).aggregate(t=Sum("hours"))["t"] or 0
        project_data.append({"project": proj, "hours": hours, "revenue": _emp_proj_revenue(employee, proj)})
    return render(request, "tracking/employee_detail.html", {"employee": employee, "project_data": project_data})


@boss_required
def employee_project_view(request, employee_id, project_id):
    employee = get_object_or_404(CustomUser, pk=employee_id)
    project = get_object_or_404(Project, pk=project_id)
    logs = Log.objects.filter(user=employee, project=project).order_by("-date")
    total_hours = logs.aggregate(t=Sum("hours"))["t"] or 0
    return render(request, "tracking/employee_project_view.html", {
        "employee": employee, "project": project, "logs": logs, "total_hours": total_hours
    })


@boss_required
def employee_log_view(request, employee_id, project_id, log_id):
    employee = get_object_or_404(CustomUser, pk=employee_id)
    project = get_object_or_404(Project, pk=project_id)
    log = get_object_or_404(Log, pk=log_id, user=employee, project=project)
    total_hours = Log.objects.filter(user=employee, project=project).aggregate(t=Sum("hours"))["t"] or 0
    return render(request, "tracking/employee_log_view.html", {
        "employee": employee, "project": project, "log": log, "total_hours": total_hours,
        "video_actions": log.video_title_actions.select_related("video_title").all(),
        "photo_progress": getattr(log, "photo_progress", None),
    })


@boss_required
def all_projects_view(request):
    projects = Project.objects.all().order_by("-created_at")
    data = [{"project": p, "total_hours": p.total_logged_hours()} for p in projects]
    return render(request, "tracking/all_projects.html", {"project_data": data})


@boss_required
def boss_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST" and "complete_project" in request.POST:
        project.is_completed = True
        project.save()
        messages.success(request, "Projekt lezárva.")
        return redirect("boss_project_view", project_id=project_id)
    members_by_role = {}
    for m in ProjectMembership.objects.filter(project=project).select_related("user"):
        role = m.user.get_job_role_display_hu()
        if role not in members_by_role:
            members_by_role[role] = []
        user_logs = Log.objects.filter(user=m.user, project=project).order_by("-date")
        members_by_role[role].append({
            "user": m.user, "logs": user_logs,
            "total_hours": user_logs.aggregate(t=Sum("hours"))["t"] or 0,
        })
    return render(request, "tracking/boss_project_view.html", {"project": project, "members_by_role": members_by_role})


@boss_required
def create_project_view(request):
    form = CreateProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        if form.cleaned_data.get("both_types"):
            project.project_type = "both"
        project.created_by = request.user
        project.save()
        messages.success(request, "Projekt sikeresen létrehozva.")
        return redirect("all_projects")
    return render(request, "tracking/create_project.html", {"form": form})


@boss_required
def new_employee_view(request):
    form = NewEmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        emp = form.save()
        messages.success(request, "Dolgozó sikeresen felvéve.")
        return redirect("employees_list")
    return render(request, "tracking/new_employee.html", {"form": form})


@login_required
def my_projects_view(request):
    user = request.user
    memberships = ProjectMembership.objects.filter(user=user).select_related("project")
    active_count = sum(1 for m in memberships if m.project.is_active)
    project_data = [{"project": m.project, "completion": m.project.completion_percentage_for_user(user)} for m in memberships]
    return render(request, "tracking/my_projects.html", {"project_data": project_data, "can_add": active_count < 3})


@login_required
def new_project_signup_view(request):
    user = request.user
    if user.job_role not in ("videos", "fotos"):
        messages.error(request, "Csak videósok és fotósok vehetnek fel új projektet.")
        return redirect("my_projects")
    my_memberships = ProjectMembership.objects.filter(user=user).select_related("project")
    occupied = set()
    for m in my_memberships:
        if m.project.videographer_date:
            occupied.add(m.project.videographer_date)
        if m.project.photo_onsite_date:
            occupied.add(m.project.photo_onsite_date)
    if user.job_role == "videos":
        available = [p for p in Project.objects.filter(project_type__in=("video", "both")).exclude(memberships__user=user)
                     if not p.is_expired and (not p.videographer_date or p.videographer_date not in occupied)]
    else:
        available = [p for p in Project.objects.filter(project_type__in=("photo", "both")).exclude(memberships__user=user)
                     if not p.is_expired and (not p.photo_onsite_date or p.photo_onsite_date not in occupied)]
    confirm_project = None
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        confirmed = request.POST.get("confirmed")
        if project_id and confirmed:
            proj = get_object_or_404(Project, pk=project_id)
            ProjectMembership.objects.get_or_create(user=user, project=proj)
            messages.success(request, "Sikeresen csatlakoztál a projekthez.")
            return redirect("my_projects")
        elif project_id:
            confirm_project = get_object_or_404(Project, pk=project_id)
    return render(request, "tracking/new_project_signup.html", {"available": available, "confirm_project": confirm_project})


@login_required
def project_page_view(request, project_id):
    user = request.user
    project = get_object_or_404(Project, pk=project_id)
    get_object_or_404(ProjectMembership, user=user, project=project)
    if not project.is_active:
        messages.warning(request, "Ez a projekt már lezárt.")
        return redirect("my_projects")
    logs = Log.objects.filter(user=user, project=project).order_by("-date")
    total_hours = logs.aggregate(t=Sum("hours"))["t"] or 0
    return render(request, "tracking/project_page.html", {"project": project, "logs": logs, "total_hours": total_hours})


@login_required
def new_log_view(request, project_id):
    user = request.user
    project = get_object_or_404(Project, pk=project_id)
    get_object_or_404(ProjectMembership, user=user, project=project)
    if not project.is_active:
        messages.warning(request, "Ez a projekt már lezárt.")
        return redirect("my_projects")
    total_so_far = Log.objects.filter(user=user, project=project).aggregate(t=Sum("hours"))["t"] or 0
    context = {"project": project, "total_hours_so_far": total_so_far, "user_role": user.job_role}
    if user.job_role == "iro":
        existing = VideoTitle.objects.filter(project=project, created_by=user).order_by("created_at")
        context["existing_titles"] = existing
        context["total_needed"] = project.required_video_count
        context["can_add_more"] = existing.count() < project.required_video_count
        context["all_titles"] = VideoTitle.objects.filter(project=project).order_by("created_at")
    elif user.job_role == "videos":
        context["pending_titles"] = VideoTitle.objects.filter(project=project, raw_uploaded=False).order_by("created_at")
    elif user.job_role == "vago":
        context["available_titles"] = VideoTitle.objects.filter(project=project, raw_uploaded=True, editing_done=False).order_by("created_at")
    if request.method == "POST":
        form = NewLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = user
            log.project = project
            log.save()
            if user.job_role == "iro":
                for t in request.POST.getlist("new_titles[]"):
                    t = t.strip()
                    if t:
                        VideoTitle.objects.create(project=project, title=t, created_by=user)
            elif user.job_role == "videos":
                for tid in request.POST.getlist("filmed_titles[]"):
                    try:
                        vt = VideoTitle.objects.get(pk=int(tid), project=project)
                        if not vt.raw_uploaded:
                            vt.raw_uploaded = True
                            vt.raw_uploaded_by = user
                            vt.raw_uploaded_at = timezone.now()
                            vt.save()
                            LogVideoTitleAction.objects.create(log=log, video_title=vt, action_type="filmed")
                    except (VideoTitle.DoesNotExist, ValueError):
                        pass
            elif user.job_role == "vago":
                for tid in request.POST.getlist("edited_titles[]"):
                    try:
                        vt = VideoTitle.objects.get(pk=int(tid), project=project, raw_uploaded=True)
                        if not vt.editing_done:
                            vt.editing_done = True
                            vt.editing_done_by = user
                            vt.editing_done_at = timezone.now()
                            vt.save()
                            LogVideoTitleAction.objects.create(log=log, video_title=vt, action_type="edited")
                    except (VideoTitle.DoesNotExist, ValueError):
                        pass
            elif user.job_role == "fotos":
                PhotoLogProgress.objects.create(
                    log=log,
                    fieldwork_done="fieldwork_done" in request.POST,
                    editing_done="editing_done" in request.POST,
                )
            messages.success(request, "Log sikeresen mentve.")
            return redirect("project_page", project_id=project_id)
        context["form"] = form
    else:
        context["form"] = NewLogForm()
    return render(request, "tracking/new_log.html", context)


@login_required
def log_detail_view(request, project_id, log_id):
    user = request.user
    project = get_object_or_404(Project, pk=project_id)
    log = get_object_or_404(Log, pk=log_id, user=user, project=project)
    total_hours = Log.objects.filter(user=user, project=project).aggregate(t=Sum("hours"))["t"] or 0
    return render(request, "tracking/log_detail.html", {
        "project": project, "log": log, "total_hours": total_hours,
        "video_actions": log.video_title_actions.select_related("video_title").all(),
        "photo_progress": getattr(log, "photo_progress", None),
    })


@login_required
def employee_autocomplete(request):
    q = request.GET.get("q", "")
    if len(q) < 1:
        return JsonResponse({"results": []})
    qs = CustomUser.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q),
        is_active=True
    )[:10]
    return JsonResponse({"results": [{"id": e.pk, "name": e.get_full_name() or e.username, "role": e.get_job_role_display_hu()} for e in qs]})


def _month_name(m):
    return ["", "Január", "Február", "Március", "Április", "Május", "Június",
            "Július", "Augusztus", "Szeptember", "Október", "November", "December"][m]


def _monthly_revenue(year, month):
    _, days = monthrange(year, month)
    labels, values = [], []
    for day in range(1, days + 1):
        d = date(year, month, day)
        rev = 0
        for log in Log.objects.filter(date__date=d).select_related("project"):
            if log.project.total_hours_expected > 0:
                rev += float(log.hours) / float(log.project.total_hours_expected) * float(log.project.revenue)
        labels.append(f"{day}.")
        values.append(round(rev))
    return {"labels": labels, "values": values}


def _user_daily_hours(user, year, month):
    _, days = monthrange(year, month)
    labels, values = [], []
    for day in range(1, days + 1):
        h = Log.objects.filter(user=user, date__date=date(year, month, day)).aggregate(t=Sum("hours"))["t"] or 0
        labels.append(f"{day}.")
        values.append(float(h))
    return {"labels": labels, "values": values}


def _emp_revenue(emp, month, year):
    total = 0
    for log in emp.logs.filter(date__month=month, date__year=year).select_related("project"):
        if log.project.total_hours_expected > 0:
            total += float(log.hours) / float(log.project.total_hours_expected) * float(log.project.revenue)
    return round(total)


def _emp_proj_revenue(emp, project):
    h = Log.objects.filter(user=emp, project=project).aggregate(t=Sum("hours"))["t"] or 0
    if project.total_hours_expected > 0:
        return round(float(h) / float(project.total_hours_expected) * float(project.revenue))
    return 0
