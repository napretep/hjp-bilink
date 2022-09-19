window.onload=()=>{
    let btn = document.querySelector('#click');
    btn.onclick=(e)=>{
        fetch("/",{
            method: 'POST',
            headers: {
      'Content-Type': 'application/json'
    },      body:JSON.stringify(
        {
            front:[
                {
                    pdfuuid:"asdasd",
                    page:9,
                    rect:[1,2,3,4],//百分比
                    occlusion:[[19,20,30,30,],[20,20,40,40]]
                },
                {
                    pdfuuid:"123546",
                    page:9,
                    rect:[1,2,3,4],//百分比
                    occlusion:[[19,20,30,30,],[20,20,40,40]]
                }
            ],
            back:[
                {
                    pdfuuid:"asdasd",
                    page:9,
                    rect:[1,2,3,4],//百分比
                    occlusion:[[19,20,30,30,],[20,20,40,40]]
                },
                {
                    pdfuuid:"123546",
                    page:9,
                    rect:[1,2,3,4],//百分比
                    occlusion:[[19,20,30,30,],[20,20,40,40]]
                }
            ],
        }
            )
        })

    }
}