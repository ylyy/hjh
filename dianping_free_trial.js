/**
 * 大众点评"免费试"自动点击脚本
 * 
 * 使用说明：
 * 1. 安装 Auto.js 或 AutoX.js (推荐)
 * 2. 授予无障碍服务权限
 * 3. 打开大众点评App，进入"免费试"页面
 * 4. 运行此脚本
 * 
 * 下载AutoX.js: https://github.com/kkevsekk1/AutoX/releases
 */

"auto";  // 自动开启无障碍服务

// ============ 配置参数 ============
const CONFIG = {
    // 点击间隔时间(毫秒)，避免操作过快被检测
    clickDelay: 1500,
    // 滑动后等待时间(毫秒)
    scrollDelay: 1000,
    // 最大滑动次数，防止无限循环
    maxScrollCount: 50,
    // 大众点评包名
    packageName: "com.dianping.v1",
    // 申请按钮的文本关键词
    applyKeywords: ["免费申请", "立即申请", "马上申请", "我要申请", "申请试用", "免费试用"],
    // 已申请/已结束的关键词(跳过这些)
    skipKeywords: ["已申请", "已结束", "已抢光", "已领取", "名额已满", "已参与"]
};

// ============ 主函数 ============
function main() {
    console.show();  // 显示控制台
    log("====== 大众点评免费试自动脚本 ======");
    log("请确保已打开大众点评的'免费试'页面");
    
    // 检查是否在大众点评App中
    if (!checkCurrentApp()) {
        toast("请先打开大众点评App！");
        log("错误：请先打开大众点评App");
        return;
    }
    
    sleep(1000);
    log("开始自动申请...");
    
    let totalClicked = 0;
    let scrollCount = 0;
    let noNewItemCount = 0;
    
    // 主循环
    while (scrollCount < CONFIG.maxScrollCount) {
        // 查找并点击当前页面的申请按钮
        let clickedThisRound = clickAllApplyButtons();
        totalClicked += clickedThisRound;
        
        if (clickedThisRound === 0) {
            noNewItemCount++;
        } else {
            noNewItemCount = 0;
        }
        
        // 如果连续3次没有新的可点击项，可能已经到底了
        if (noNewItemCount >= 3) {
            log("连续多次未发现新的申请按钮，可能已经全部申请完成");
            break;
        }
        
        // 向下滑动加载更多
        log("向下滑动加载更多...");
        scrollDown();
        sleep(CONFIG.scrollDelay);
        scrollCount++;
    }
    
    log("====== 脚本执行完成 ======");
    log("共点击申请按钮: " + totalClicked + " 次");
    log("滑动次数: " + scrollCount);
    toast("完成！共申请 " + totalClicked + " 个");
}

// ============ 检查当前App ============
function checkCurrentApp() {
    let currentPackage = currentPackage();
    if (currentPackage === CONFIG.packageName) {
        return true;
    }
    // 有时候获取包名可能不准确，也可以通过页面元素判断
    let dianpingElement = text("大众点评").findOne(1000) || 
                          id("com.dianping.v1:id").findOne(1000);
    return dianpingElement !== null;
}

// ============ 点击所有申请按钮 ============
function clickAllApplyButtons() {
    let clickedCount = 0;
    
    // 遍历所有申请关键词
    for (let keyword of CONFIG.applyKeywords) {
        let buttons = text(keyword).find();
        
        for (let i = 0; i < buttons.length; i++) {
            let btn = buttons[i];
            
            // 检查按钮是否可见且可点击
            if (btn && btn.visibleToUser() && isClickableButton(btn)) {
                // 检查是否应该跳过（已申请等状态）
                if (!shouldSkip(btn)) {
                    log("找到按钮: " + keyword);
                    
                    // 点击按钮
                    let clicked = clickButton(btn);
                    if (clicked) {
                        clickedCount++;
                        log("成功点击: " + keyword);
                        sleep(CONFIG.clickDelay);
                        
                        // 处理可能出现的弹窗
                        handlePopup();
                    }
                }
            }
        }
    }
    
    // 也尝试通过控件类型查找按钮
    let allButtons = className("android.widget.Button").find();
    for (let btn of allButtons) {
        let btnText = btn.text();
        for (let keyword of CONFIG.applyKeywords) {
            if (btnText && btnText.includes(keyword) && !shouldSkipByText(btnText)) {
                if (btn.visibleToUser()) {
                    log("找到按钮(Button类型): " + btnText);
                    let clicked = clickButton(btn);
                    if (clicked) {
                        clickedCount++;
                        sleep(CONFIG.clickDelay);
                        handlePopup();
                    }
                }
            }
        }
    }
    
    return clickedCount;
}

// ============ 判断是否可点击 ============
function isClickableButton(node) {
    if (!node) return false;
    // 检查是否可点击
    return node.clickable() || (node.parent() && node.parent().clickable());
}

// ============ 判断是否应该跳过 ============
function shouldSkip(node) {
    if (!node) return true;
    
    // 检查按钮本身的文本
    let text = node.text();
    if (shouldSkipByText(text)) return true;
    
    // 检查父节点和兄弟节点
    let parent = node.parent();
    if (parent) {
        let parentText = parent.text();
        if (shouldSkipByText(parentText)) return true;
        
        // 检查兄弟节点
        for (let i = 0; i < parent.childCount(); i++) {
            let sibling = parent.child(i);
            if (sibling && shouldSkipByText(sibling.text())) {
                return true;
            }
        }
    }
    
    return false;
}

function shouldSkipByText(text) {
    if (!text) return false;
    for (let keyword of CONFIG.skipKeywords) {
        if (text.includes(keyword)) {
            return true;
        }
    }
    return false;
}

// ============ 点击按钮 ============
function clickButton(node) {
    try {
        // 尝试直接点击
        if (node.clickable()) {
            return node.click();
        }
        
        // 尝试点击父节点
        let parent = node.parent();
        if (parent && parent.clickable()) {
            return parent.click();
        }
        
        // 使用坐标点击
        let bounds = node.bounds();
        if (bounds) {
            let x = bounds.centerX();
            let y = bounds.centerY();
            return click(x, y);
        }
    } catch (e) {
        log("点击失败: " + e);
    }
    return false;
}

// ============ 处理弹窗 ============
function handlePopup() {
    sleep(500);
    
    // 常见的确认弹窗按钮
    let confirmKeywords = ["确定", "确认", "知道了", "好的", "立即申请", "提交"];
    
    for (let keyword of confirmKeywords) {
        let confirmBtn = text(keyword).findOne(500);
        if (confirmBtn && confirmBtn.visibleToUser()) {
            log("处理弹窗: " + keyword);
            clickButton(confirmBtn);
            sleep(300);
        }
    }
    
    // 处理可能的关闭按钮
    let closeBtn = desc("关闭").findOne(300) || id("close").findOne(300);
    if (closeBtn) {
        clickButton(closeBtn);
    }
}

// ============ 向下滑动 ============
function scrollDown() {
    let height = device.height;
    let width = device.width;
    
    // 从屏幕中下部向上滑动
    let startX = width / 2;
    let startY = height * 0.7;
    let endY = height * 0.3;
    
    swipe(startX, startY, startX, endY, 500);
}

// ============ 启动脚本 ============
// 设置脚本运行时不受音量键影响
events.on("volume_up", function(e) {
    log("音量+键按下，停止脚本");
    engines.stopAll();
    exit();
});

log("提示: 按音量+键可随时停止脚本");
sleep(2000);

// 运行主函数
main();
