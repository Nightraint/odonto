function select2(select){
    select.select2({
        tags:true,
        placeholder: 'Haga click para seleccionar',
        allowClear: true,
        language: 'es',
    });
}

function monthStr(monthNumber){
    switch (monthNumber){
        case '01':
            return 'Enero';
        case '02':
            return 'Feb.';
        case '03':
            return 'Marzo';
        case '04':
            return 'Abril';
        case '05':
            return 'Mayo';
        case '06':
            return 'Junio';
        case '07':
            return 'Julio';
        case '08':
            return 'Ago.';
        case '09':
            return 'Set.';
        case '10':
            return 'Oct.';
        case '11':
            return 'Nov.';
        case '12':
            return 'Dic.';
    }
}
