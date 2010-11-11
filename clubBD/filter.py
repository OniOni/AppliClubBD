import gobject

class FilterCollection(object):
    def __init__(self, models, filter_timeout):
        self._models = models

        self._value = ''
        self._text = None
        self._obj = None
        
        self._user_loan = None
        self._text_loan = ''
        self._value_user = ''

        self._models['authors'].filter_func = self._func_author
        self._models['editors'].filter_func = self._func_editor
        self._models['serials'].filter_func = self._func_serial
        self._models['books'].filter_func = self._func_book
        self._models['loans'].filter_func = self._func_loan
        self._models['users'].filter_func = self._func_user

        self._timeout_value = 0
        
        self._f_to_refilter = set()

        # Loans must be pre-filtered
        self._models['loans'].refilter()

        self._filter_timeout = filter_timeout

    def refilter_value(self, value):
        self._value = value
        self._timeout(self._refilter_collection)
  
    def refilter_obj(self, obj):
        self._obj = obj
        self._timeout(self._models['books'].refilter)
        
    def refilter_text(self,text):
        self._text = text
        self._timeout(self._models['books'].refilter)

    def refilter_loans(self, user):
        self._user_loan = user
        self._timeout(self._models['loans'].refilter)

    def refilter_loans_text(self,text):
        self._text_loan = text
        self._timeout(self._models['loans'].refilter)

    def refilter_user(self,value):
        self._value_user = value
        self._timeout(self._models['users'].refilter)

    def _timeout(self,f):
        self._f_to_refilter.add(f)
        if self._timeout_value:
            gobject.source_remove(self._timeout_value)
        self._timeout_value = gobject.timeout_add(self._filter_timeout,self._timeout_end)

    def _timeout_end(self):
        for f in self._f_to_refilter:
            f()
        self._f_to_refilter.clear()

    def _refilter_collection(self):
        self._models['authors'].refilter()
        self._models['editors'].refilter()
        self._models['serials'].refilter()

    def _func_author(self,obj):
        return self._value in obj.name.lower()

    _func_editor = _func_author

    def _func_serial(self,obj):
        return self._value in obj.title.lower() or any(self._value in pre for pre in obj.prefix)

    def _func_book(self,obj):
        if self._text and (not obj.reference.startswith(self._text) and self._text not in obj.title.lower()):
            return False
        if self._obj and (self._obj not in obj.authors + [obj.serial,obj.editor]):
            return False
        return True

    def _func_loan(self,obj):
        match_text = obj.reference.startswith(self._text_loan)
        match_text_strict = match_text and len(self._text_loan) > 0

        is_loan = bool(obj.user)
        match_user = self._user_loan == obj.user

        if not self._user_loan:
            return is_loan and match_text
        else:
            return (not is_loan and match_text_strict) or (is_loan and match_user)
                
    def _func_user(self,obj):
        return self._value_user == str(obj.id) or self._value_user in obj.firstname.lower() or self._value_user in obj.lastname.lower()
