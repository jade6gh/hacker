#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <libxml/HTMLparser.h>
#include <libxml/xpath.h>

// 存储下载数据
struct MemoryStruct {
    char *memory;
    size_t size;
};

// 存储图片URL
struct ImgList {
    char **urls;
    size_t count;
};

// libcurl写回调函数
static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)userp;

    mem->memory = realloc(mem->memory, mem->size + realsize + 1);
    if (mem->memory == NULL) {
        fprintf(stderr, "内存不足!\n");
        return 0;
    }

    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
}

// 解析HTML提取图片URL
struct ImgList parse_html_for_images(const char *html_content) {
    struct ImgList list = {NULL, 0};
    htmlDocPtr doc = htmlReadDoc((const xmlChar *)html_content, NULL, NULL, HTML_PARSE_RECOVER | HTML_PARSE_NOERROR | HTML_PARSE_NOWARNING);
    
    if (!doc) {
        fprintf(stderr, "无法解析HTML文档\n");
        return list;
    }

    xmlXPathContextPtr context = xmlXPathNewContext(doc);
    if (!context) {
        fprintf(stderr, "无法创建XPath上下文\n");
        xmlFreeDoc(doc);
        return list;
    }

    // 查找所有img标签
    xmlXPathObjectPtr result = xmlXPathEvalExpression((xmlChar *)"//img/@src", context);
    if (!result) {
        fprintf(stderr, "XPath查询失败\n");
        xmlXPathFreeContext(context);
        xmlFreeDoc(doc);
        return list;
    }

    // 提取图片URL
    if (result->type == XPATH_NODESET) {
        xmlNodeSetPtr nodeset = result->nodesetval;
        list.count = nodeset->nodeNr;
        list.urls = malloc(list.count * sizeof(char *));
        
        for (int i = 0; i < list.count; ++i) {
            xmlNodePtr node = nodeset->nodeTab[i];
            if (node->type == XML_ATTRIBUTE_NODE) {
                xmlChar *value = xmlNodeListGetString(node->doc, node->children, 1);
                list.urls[i] = strdup((char *)value);
                xmlFree(value);
            }
        }
    }

    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
    xmlFreeDoc(doc);
    return list;
}

// 下载并保存图片
int download_image(const char *url, const char *filename, const char *referer) {
    CURL *curl;
    FILE *fp;
    CURLcode res;
    
    curl = curl_easy_init();
    if (!curl) {
        fprintf(stderr, "无法初始化CURL\n");
        return 1;
    }

    fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "无法创建文件 %s\n", filename);
        curl_easy_cleanup(curl);
        return 1;
    }

    // 设置CURL选项
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
    
    if (referer) {
        struct curl_slist *headers = NULL;
        char referer_header[256];
        snprintf(referer_header, sizeof(referer_header), "Referer: %s", referer);
        headers = curl_slist_append(headers, referer_header);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    }

    // 设置代理（如果需要）
    // curl_easy_setopt(curl, CURLOPT_PROXY, "http://proxy-ip:port");
    
    // 执行下载
    res = curl_easy_perform(curl);
    fclose(fp);
    
    if (res != CURLE_OK) {
        fprintf(stderr, "下载失败: %s\n", curl_easy_strerror(res));
        remove(filename);
    }

    curl_easy_cleanup(curl);
    return res;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "用法: %s <目标URL>\n", argv[0]);
        return 1;
    }

    const char *url = argv[1];
    CURL *curl;
    CURLcode res;
    struct MemoryStruct chunk = {NULL, 0};

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    
    if (!curl) {
        fprintf(stderr, "无法初始化CURL\n");
        return 1;
    }

    // 设置CURL选项
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &chunk);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    
    // 设置代理（如果需要）
    // curl_easy_setopt(curl, CURLOPT_PROXY, "http://proxy-ip:port");

    // 执行请求
    res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        fprintf(stderr, "请求失败: %s\n", curl_easy_strerror(res));
        curl_easy_cleanup(curl);
        free(chunk.memory);
        return 1;
    }

    // 解析HTML获取图片URL
    struct ImgList images = parse_html_for_images(chunk.memory);
    printf("找到 %zu 张图片\n", images.count);

    // 创建保存目录
    system("mkdir -p downloaded_images");

    // 下载每张图片
    for (size_t i = 0; i < images.count; ++i) {
        char filename[256];
        snprintf(filename, sizeof(filename), "downloaded_images/image_%zu.jpg", i);
        
        printf("正在下载: %s\n", images.urls[i]);
        if (download_image(images.urls[i], filename, url) == CURLE_OK) {
            printf("保存为: %s\n", filename);
        }
        
        free(images.urls[i]);
    }

    // 清理
    free(images.urls);
    curl_easy_cleanup(curl);
    free(chunk.memory);
    curl_global_cleanup();
    return 0;
}