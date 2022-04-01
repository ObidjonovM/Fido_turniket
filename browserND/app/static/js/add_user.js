function getOptionValue1(sel) {
    let login = document.getElementById('login');
    let hidden_dept_id = document.getElementById('hidden_dept_id');
    let hidden_job_id = document.getElementById('hidden_job_id');
    login.value = makeUsername(transliterate(sel.options[sel.selectedIndex].text));
    hidden_dept_id.value = sel.options[sel.selectedIndex].getAttribute('dept_id');
    hidden_job_id.value = sel.options[sel.selectedIndex].getAttribute('job_id');
}


function transliterate(word){
    var answer = ""
      , a = {};

   a["Ё"]="Yo";a["Й"]="I";a["Ц"]="Ts";a["У"]="U";a["К"]="K";a["Е"]="E";a["Н"]="N";a["Г"]="G";a["Ш"]="Sh";a["Щ"]="Sh";a["З"]="Z";a["Х"]="H";a["Ъ"]="";
   a["ё"]="yo";a["й"]="i";a["ц"]="ts";a["у"]="u";a["к"]="k";a["е"]="e";a["н"]="n";a["г"]="g";a["ш"]="sh";a["щ"]="sh";a["з"]="z";a["х"]="h";a["ъ"]="";
   a["Ф"]="F";a["Ы"]="I";a["В"]="V";a["А"]="a";a["П"]="P";a["Р"]="R";a["О"]="O";a["Л"]="L";a["Д"]="D";a["Ж"]="J";a["Э"]="E";
   a["ф"]="f";a["ы"]="i";a["в"]="v";a["а"]="a";a["п"]="p";a["р"]="r";a["о"]="o";a["л"]="l";a["д"]="d";a["ж"]="j";a["э"]="e";
   a["Я"]="Ya";a["Ч"]="Ch";a["С"]="S";a["М"]="M";a["И"]="I";a["Т"]="T";a["Ь"]="";a["Б"]="B";a["Ю"]="Yu";
   a["я"]="ya";a["ч"]="ch";a["с"]="s";a["м"]="m";a["и"]="i";a["т"]="t";a["ь"]="";a["б"]="b";a["ю"]="yu";

   for (i in word){
     if (word.hasOwnProperty(i)) {
       if (a[word[i]] === undefined){
         answer += word[i];
       } else {
         answer += a[word[i]];
       }
     }
   }
   return answer;
}


function makeUsername(fullname) {
    fullnameList = fullname.split(" ");
    return fullnameList[1].toLowerCase() + "." + fullnameList[0].toLowerCase();
}