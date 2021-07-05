
METRICS = {}
METRICS_ALIAS_MAP = {}

class MetricManager(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        pass

    # function register
    def register(self, name, config, desc="", public=False, alias=None):
        def deco(func):
            metric = {
                'config': config,
                'description': desc,
                'alias': alias if alias is not None else [],
                'method': func,
                'public': public,
            }
            METRICS[name] = metric
            for alia in alias:
                METRICS_ALIAS_MAP[alia] = metric
            return func
        return deco

    def get_root_metric(self, metric):
        if metric in METRICS_ALIAS_MAP:
            return METRICS_ALIAS_MAP[metric]
        elif metric in METRICS:
            return metric

    def get_metric_config(self, metric):
        return METRICS[self.get_root_metric(metric)]

    def get_metric_summary(self, with_description):
        summary = ''
        if with_description:
            for metric in METRICS:
                if METRICS[metric].get('public', False):
                    description = METRICS[metric]['description']
                    summary += '[{}]: '.format(metric) + (description if description else '[No description]') + '\n'
        else:
            summary = ', '.join((filter(lambda m: METRICS[m].get('public', False), METRICS.keys())))

        return summary

    def get_metric_method(self, metric):
        return self.get_metric_config(metric)['method']

# get metric manager
def get_metric_manager():
    return MetricManager()