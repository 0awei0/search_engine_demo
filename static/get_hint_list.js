function send_info() {
    const search_info = $("#search").val();

    const data = {
        data: JSON.stringify({
            'data': search_info,
        }),
    }

    //ajax 提交数据
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/words_hint", //后端请求url
        data: data,
        success:
            function (result) {
                $('#hint_list').html('');
                ul.style.display = 'block';
                const ans = result['hint_list']
                let len = ans.length;

                if (len > 0) {
                    for (let i = 0; i < len; i++) {
                        // console.log('ans[i]: ', ans[i]);
                        // "<div onclick=func('" + tmp + "')>点击弹出数据及其类型</div>";
                        $("#hint_list").append("<li><a href='javascript:void(0);' onclick=get_ans('" + ans[i] + "')>" + ans[i] + '</a></li>');
                    }
                }
            },
        error: function () {
            // console.log('请求失败！\n');
        }
    })
}

function get_ans(message) {
    const data = {
        data: JSON.stringify({
            'data': message,
        }),
    }
    console.log("send info: ", message);
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/render_hint_list", //后端请求url
        data: data,
        success: function (result) {
            console.log(result['message'] + 'request success!');
            window.location.href = "/results/" + message;
        },
        error: function () {
            console.log('请求失败！\n');
        }
    })
}

