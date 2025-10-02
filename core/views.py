from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Avg, Max, Min, Count
from datetime import datetime, timedelta
import csv, io

from .forms import DailyMetricForm, UploadFileForm
from .models import DailyMetric

@login_required(login_url='/admin/login/')
def home(request):
    return redirect('dashboard')

@login_required(login_url='/admin/login/')
def add_metric(request):
    if request.method == 'POST':
        form = DailyMetricForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Data saved successfully!")
            return redirect('add_metric')
    else:
        form = DailyMetricForm()
    return render(request, 'add_metric.html', {'form': form})

@login_required(login_url='/admin/login/')
def import_csv(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            try:
                text = f.read().decode('utf-8', errors='ignore')
                reader = csv.DictReader(io.StringIO(text))
                count = 0
                for row in reader:
                    date = row['date']
                    weight = float(row.get('weight') or 0)
                    steps = int(float(row.get('steps') or 0))
                    calories = int(float(row.get('calories') or 0))
                    DailyMetric.objects.update_or_create(
                        user=request.user, date=date,
                        defaults={'weight': weight, 'steps': steps, 'calories': calories}
                    )
                    count += 1
                messages.success(request, f"Import successful: {count} rows.")
            except Exception as e:
                messages.error(request, f"Import failed: {e}")
            return redirect('import_csv')
    else:
        form = UploadFileForm()
    return render(request, 'import_csv.html', {'form': form})

@login_required(login_url='/admin/login/')
def dashboard(request):
    # Last 30 days
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)
    qs = DailyMetric.objects.filter(user=request.user, date__gte=start_date, date__lte=end_date).order_by('date')

    dates = [m.date.strftime("%Y-%m-%d") for m in qs]
    weights = [m.weight for m in qs]

    def ma(arr, w):
        out = []
        for i in range(len(arr)):
            if i < w-1:
                out.append(None)
            else:
                out.append(round(sum(arr[i-w+1:i+1]) / w, 2))
        return out

    data = {
        'dates': dates,
        'weights': weights,
        'ma7': ma(weights, 7),
        'ma30': ma(weights, 30),
    }
    return render(request, 'dashboard.html', data)

@login_required(login_url='/admin/login/')
def data_list(request):
    """显示用户所有健身数据记录，支持分页和排序"""
    order_by = request.GET.get('order_by', '-date')  # 默认按日期倒序
    search_date = request.GET.get('search_date', '')
    
    # 基础查询
    queryset = DailyMetric.objects.filter(user=request.user)
    
    # 日期搜索
    if search_date:
        queryset = queryset.filter(date=search_date)
    
    # 排序
    if order_by in ['date', '-date', 'weight', '-weight', 'steps', '-steps', 'calories', '-calories']:
        queryset = queryset.order_by(order_by)
    else:
        queryset = queryset.order_by('-date')
    
    # 分页
    paginator = Paginator(queryset, 10)  # 每页显示10条记录
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'order_by': order_by,
        'search_date': search_date,
    }
    return render(request, 'data_list.html', context)

@login_required(login_url='/admin/login/')  
def data_detail(request, pk):
    """查看单条记录详情"""
    metric = get_object_or_404(DailyMetric, pk=pk, user=request.user)
    return render(request, 'data_detail.html', {'metric': metric})

@login_required(login_url='/admin/login/')
def data_stats(request):
    """数据统计视图"""
    # 基础统计
    stats = DailyMetric.objects.filter(user=request.user).aggregate(
        total_records=Count('id'),
        avg_weight=Avg('weight'),
        max_weight=Max('weight'),
        min_weight=Min('weight'),
        avg_steps=Avg('steps'),
        max_steps=Max('steps'),
        avg_calories=Avg('calories'),
        max_calories=Max('calories'),
    )
    
    # 最近30天统计
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)
    recent_stats = DailyMetric.objects.filter(
        user=request.user, 
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(
        recent_records=Count('id'),
        recent_avg_weight=Avg('weight'),
        recent_avg_steps=Avg('steps'),
        recent_avg_calories=Avg('calories'),
    )
    
    # 最早和最新记录
    first_record = DailyMetric.objects.filter(user=request.user).order_by('date').first()
    latest_record = DailyMetric.objects.filter(user=request.user).order_by('-date').first()
    
    context = {
        'stats': stats,
        'recent_stats': recent_stats,
        'first_record': first_record,
        'latest_record': latest_record,
    }
    return render(request, 'data_stats.html', context)
