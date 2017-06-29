from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from back.views.AuthAccount import AuthAccount
from django.utils.decorators import method_decorator
from dbms.tasks import get_matedata
import json


@method_decorator(AuthAccount, name='dispatch')
class GetMetaData(View):
    def get(self, request):
        host_ip = request.GET.get('host_ip', None)
        table_schema = request.GET.get('table_schema', None)
        db_info = None
        table_list = None
        if not host_ip:
            host_info = models.HostInfo.objects.filter(app_type__app_name='MySQL').values('host_ip')
            return render(request, 'get_metadata.html', {'host_info': host_info})
        # ajax 请求获取数据
        result_dict = {'db_info': [], 'table_info': []}
        if host_ip:
            db_list = models.MetaDataDatabase.objects.filter(host_ip=host_ip).all()
            for item in db_list:
                result_dict['db_info'].append(item.schema_name)
        if table_schema:
            table_list = models.MetaDataTables.objects.filter(host_ip=host_ip, table_schema=table_schema).all()
            for item in table_list:
                result_dict['table_info'].append(item.table_name)

        return HttpResponse(json.dumps(result_dict))

    def post(self, request):
        account_list = models.HostAPPAccount.objects.values('host__host_ip',
                                                            'host__host_user',
                                                            'host__host_port',
                                                            'host__host_pass',
                                                            'app_port',
                                                            'app_pass',
                                                            'app_user'
                                                            )

        get_matedata(account_list)
        return HttpResponse('ok')


@method_decorator(AuthAccount, name='dispatch')
class CollectMetadata(View):
    def get(self, request):
        return render(request, 'collect_metadata.html')

    def post(self, request):
        account_list = models.HostAPPAccount.objects.values('host__host_ip',
                                                            'host__host_user',
                                                            'host__host_port',
                                                            'host__host_pass',
                                                            'app_port',
                                                            'app_pass',
                                                            'app_user'
                                                            )

        get_matedata(account_list)
        return HttpResponse('ok')


@method_decorator(AuthAccount, name='dispatch')
class GetTableInfo(View):
    def get(self, request):
        result_dict = {'table_info': {},
                       'column_info': {},
                       'index_info': {},
                       'table_sc': {'sql_content': ''}
                       }
        host_ip = request.GET.get('host_ip', None)
        table_schema = request.GET.get('table_schema', None)
        table_name = request.GET.get('table_name', None)
        table_info = models.MetaDataTables.objects.filter(host_ip=host_ip,
                                                          table_schema=table_schema,
                                                          table_name=table_name).all()
        column_info = models.MetaDataColumns.objects.filter(host_ip=host_ip,
                                                            table_schema=table_schema,
                                                            table_name=table_name).all()
        index_info = models.MetaDataIndexs.objects.filter(host_ip=host_ip,
                                                          table_schema=table_schema,
                                                          table_name=table_name).all()
        table_sc = models.MetaDataTableStructure.objects.filter(table__host_ip=host_ip).all()
        for item in table_info:
            result_dict['table_info']['table_name'] = item.table_name
            result_dict['table_info']['engine'] = item.engine
            result_dict['table_info']['row_format'] = item.row_format
            result_dict['table_info']['table_rows'] = item.table_rows
            result_dict['table_info']['avg_row_length'] = item.avg_row_length
            result_dict['table_info']['max_data_length'] = item.max_data_length
            result_dict['table_info']['data_length'] = item.data_length
            result_dict['table_info']['index_length'] = item.index_length
            result_dict['table_info']['data_free'] = item.data_free
            result_dict['table_info']['chip_size'] = item.chip_size
            result_dict['table_info']['auto_increment'] = item.auto_increment
            result_dict['table_info']['table_collation'] = item.table_collation
            result_dict['table_info']['create_time'] = str(item.create_time)
            result_dict['table_info']['create_time'] = str(item.create_time)
            result_dict['table_info']['check_time'] = str(item.check_time)
            result_dict['table_info']['table_comment'] = item.table_comment

        for item in column_info:
            result_dict['column_info']['column_name'] = item.column_name
            result_dict['column_info']['column_type'] = item.column_type
            result_dict['column_info']['collation_name'] = item.collation_name
            result_dict['column_info']['is_nullable'] = item.is_nullable
            result_dict['column_info']['column_key'] = item.column_key
            result_dict['column_info']['column_default'] = item.column_default
            result_dict['column_info']['extra'] = item.extra
            result_dict['column_info']['privileges'] = item.privileges
            result_dict['column_info']['column_comment'] = item.column_comment

        for item in index_info:
            result_dict['index_info']['column_name'] = item.column_name
            result_dict['index_info']['non_unique'] = item.non_unique
            result_dict['index_info']['index_name'] = item.index_name
            result_dict['index_info']['seq_in_index'] = item.seq_in_index
            result_dict['index_info']['cardinality'] = item.cardinality
            result_dict['index_info']['nullable'] = item.nullable
            result_dict['index_info']['index_type'] = item.index_type
            result_dict['index_info']['index_comment'] = item.index_comment

        for item in table_sc:
            result_dict['table_sc']['sql_content'] = item.content
        return HttpResponse(json.dumps(result_dict))
