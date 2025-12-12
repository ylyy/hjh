/**
 * 大众点评"免费试"自动点击脚本
 * 适用于: Hamibot (推荐) / Auto.js Pro
 * 
 * Hamibot下载: https://hamibot.com/
 */

"auto";

var CONFIG = {
    clickDelay: 1500,
    scrollDelay: 1000,
    maxScrollCount: 50,
    applyKeywords: ["免费申请", "立即申请", "马上申请", "我要申请", "申请试用", "免费试用", "立即领取"],
    skipKeywords: ["已申请", "已结束", "已抢光", "已领取", "名额已满", "已参与"]
};

function main() {
    console.show();
    log("====== 大众点评免费试脚本 ======");
    log("请确保已打开'免费试'页面");
    sleep(2000);
    
    var totalClicked = 0;
    var scrollCount = 0;
    var noNewCount = 0;
    
    while (scrollCount < CONFIG.maxScrollCount) {
        var clicked = clickApplyButtons();
        totalClicked = totalClicked + clicked;
        
        if (clicked === 0) {
            noNewCount++;
        } else {
            noNewCount = 0;
        }
        
        if (noNewCount >= 3) {
            log("未发现新按钮，可能已完成");
            break;
        }
        
        scrollDown();
        sleep(CONFIG.scrollDelay);
        scrollCount++;
    }
    
    log("完成！共申请: " + totalClicked + " 个");
    toast("完成！共申请 " + totalClicked + " 个");
}

function clickApplyButtons() {
    var count = 0;
    
    for (var i = 0; i < CONFIG.applyKeywords.length; i++) {
        var keyword = CONFIG.applyKeywords[i];
        var buttons = text(keyword).find();
        
        for (var j = 0; j < buttons.length; j++) {
            var btn = buttons[j];
            if (btn) {
                if (btn.visibleToUser()) {
                    if (!shouldSkip(btn)) {
                        log("点击: " + keyword);
                        
                        if (btn.clickable()) {
                            btn.click();
                        } else {
                            var btnParent = btn.parent();
                            if (btnParent) {
                                if (btnParent.clickable()) {
                                    btnParent.click();
                                } else {
                                    var b = btn.bounds();
                                    click(b.centerX(), b.centerY());
                                }
                            } else {
                                var b = btn.bounds();
                                click(b.centerX(), b.centerY());
                            }
                        }
                        
                        count++;
                        sleep(CONFIG.clickDelay);
                        handlePopup();
                    }
                }
            }
        }
    }
    return count;
}

function shouldSkip(node) {
    var text = node.text();
    if (!text) {
        text = "";
    }
    
    var parent = node.parent();
    var parentText = "";
    if (parent) {
        var pText = parent.text();
        if (pText) {
            parentText = pText;
        }
    }
    
    for (var i = 0; i < CONFIG.skipKeywords.length; i++) {
        var kw = CONFIG.skipKeywords[i];
        if (text.includes(kw)) {
            return true;
        }
        if (parentText.includes(kw)) {
            return true;
        }
    }
    return false;
}

function handlePopup() {
    sleep(500);
    var confirms = ["确定", "确认", "知道了", "好的", "提交"];
    for (var i = 0; i < confirms.length; i++) {
        var c = confirms[i];
        var btn = text(c).findOne(300);
        if (btn) {
            btn.click();
            sleep(300);
        }
    }
}

function scrollDown() {
    var h = device.height;
    var w = device.width;
    swipe(w/2, h*0.7, w/2, h*0.3, 400);
}

events.on("volume_up", function() { 
    engines.stopAll(); 
    exit(); 
});
log("按音量+键停止脚本");

main();
