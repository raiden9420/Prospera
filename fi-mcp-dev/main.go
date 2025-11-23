package main

import (
    "context"
    "encoding/json"
    "fmt"
    "html/template"
    "log"
    "net/http"
    "os"
    "strconv"
    "strings"
    "time"

    "github.com/epifi/fi-mcp-lite/middlewares"
    "github.com/epifi/fi-mcp-lite/pkg"
)

var (
    authMW        = middlewares.NewAuthMiddleware()
    googleAPIKey  string
)

func main() {

    mux := http.NewServeMux()

    // ————— Login UI —————
    mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
    mux.HandleFunc("/mockWebPage", webPageHandler)
    mux.HandleFunc("/login", loginHandler)

    // ————— Polling JSON endpoints —————
    mux.Handle("/ask-ai", withAuth(http.HandlerFunc(askAIHandler)))
    mux.Handle("/quick-insights", withAuth(http.HandlerFunc(quickInsightsHandler)))
    mux.Handle("/api/net_worth", withAuth(apiHandler("fetch_net_worth.json")))
    mux.Handle("/api/credit_report", withAuth(apiHandler("fetch_credit_report.json")))
    mux.Handle("/api/epf_details", withAuth(apiHandler("fetch_epf_details.json")))
    mux.Handle("/api/mf_transactions", withAuth(apiHandler("fetch_mf_transactions.json")))
    mux.Handle("/api/bank_transactions", withAuth(apiHandler("fetch_bank_transactions.json")))
    mux.Handle("/api/stock_transactions", withAuth(apiHandler("fetch_stock_transactions.json")))


    // ————— SSE streaming endpoints —————
    mux.Handle("/stream/net_worth", withAuth(sseStream("fetch_net_worth.json", 2*time.Second)))
    mux.Handle("/stream/credit_report", withAuth(sseStream("fetch_credit_report.json", 5*time.Second)))
    mux.Handle("/stream/epf_details", withAuth(sseStream("fetch_epf_details.json", 2*time.Second)))
    mux.Handle("/stream/mf_transactions", withAuth(sseStream("fetch_mf_transactions.json", 2*time.Second)))
    mux.Handle("/stream/bank_transactions", withAuth(sseStream("fetch_bank_transactions.json", 2*time.Second)))
    mux.Handle("/stream/stock_transactions", withAuth(sseStream("fetch_stock_transactions.json", 2*time.Second)))
    

    port := pkg.GetPort()
    log.Printf("Listening on :%s\n", port)
    log.Fatal(http.ListenAndServe(":"+port, mux))
}

func askAIHandler(w http.ResponseWriter, r *http.Request) {
    var requestBody struct {
        Query string `json:"query"`
    }
    if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    phone := r.Context().Value("phone").(string)
    query := strings.ToLower(requestBody.Query)
    var responseText string

    if strings.Contains(query, "invest") {
        netWorthData, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/fetch_net_worth.json", phone))
        if err != nil {
            responseText = "I need your net worth information to provide investment suggestions."
        } else {
            var netWorth struct {
                NetWorthResponse struct {
                    AssetValues []struct {
                        AssetType string `json:"netWorthAttribute"`
                        Value     struct {
                            Units string `json:"units"`
                        } `json:"value"`
                    } `json:"assetValues"`
                } `json:"netWorthResponse"`
            }
            json.Unmarshal(netWorthData, &netWorth)

            var totalAssets float64
            assetValues := make(map[string]float64)
            for _, asset := range netWorth.NetWorthResponse.AssetValues {
                val, _ := strconv.ParseFloat(asset.Value.Units, 64)
                assetValues[asset.AssetType] = val
                totalAssets += val
            }

            if totalAssets > 0 {
                if assetValues["ASSET_TYPE_MUTUAL_FUND"]/totalAssets > 0.7 {
                    responseText = "Your portfolio is heavily weighted towards mutual funds. To diversify, you could consider exploring other asset classes like stocks or ETFs."
                } else if assetValues["ASSET_TYPE_DEPOSITS"]/totalAssets > 0.7 {
                    responseText = "A significant portion of your assets are in deposits. For potentially higher growth, you could explore investing in a diversified portfolio of mutual funds."
                } else {
                    responseText = "A balanced portfolio is a great foundation. To optimize further, you could consider a strategic mix of equity for growth and debt mutual funds for stability."
                }
            } else {
                responseText = "It looks like you haven't connected any assets yet. Once you connect your accounts, I can provide investment suggestions."
            }
        }
    } else if strings.Contains(query, "financial status") {
        netWorthData, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/fetch_net_worth.json", phone))
        var netWorthValue string
        if err == nil {
            var netWorth struct {
                NetWorthResponse struct {
                    TotalNetWorthValue struct {
                        Units string `json:"units"`
                    } `json:"totalNetWorthValue"`
                } `json:"netWorthResponse"`
            }
            json.Unmarshal(netWorthData, &netWorth)
            if netWorth.NetWorthResponse.TotalNetWorthValue.Units != "" {
                netWorthValue = netWorth.NetWorthResponse.TotalNetWorthValue.Units
            }
        }

        creditReportData, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/fetch_credit_report.json", phone))
        var creditScore int
        if err == nil {
            var creditReport struct {
                CreditReportResponse struct {
                    CreditScore struct {
                        Value int `json:"value"`
                    } `json:"creditScore"`
                } `json:"creditReportResponse"`
            }
            json.Unmarshal(creditReportData, &creditReport)
            if creditReport.CreditReportResponse.CreditScore.Value != 0 {
                creditScore = creditReport.CreditReportResponse.CreditScore.Value
            }
        }

        responseText = "Here's a summary of your current financial status:\n"
        if netWorthValue != "" {
            responseText += fmt.Sprintf("- Your total net worth is approximately %s INR.\n", netWorthValue)
        }
        if creditScore != 0 {
            responseText += fmt.Sprintf("- Your credit score is %d, which is considered good.", creditScore)
        }

    } else if strings.Contains(query, "net worth") {
        fileData, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/fetch_net_worth.json", phone))
        if err != nil {
            responseText = "I could not find your net worth information."
        } else {
            var jsonData map[string]interface{}
            json.Unmarshal(fileData, &jsonData)
            formatted, _ := json.MarshalIndent(jsonData, "", "  ")
            responseText = string(formatted)
        }
    } else if strings.Contains(query, "transactions") {
        fileData, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/fetch_bank_transactions.json", phone))
        if err != nil {
            responseText = "I could not find your transaction information."
        } else {
            var jsonData map[string]interface{}
            json.Unmarshal(fileData, &jsonData)
            formatted, _ := json.MarshalIndent(jsonData, "", "  ")
            responseText = string(formatted)
        }
    } else {
        responseText = "I'm sorry, I'm not able to answer that question right now. As a mock server for testing, I can provide insights on your financial status, investment suggestions, net worth, and transactions. Please try asking about one of those topics."
    }

    response := map[string]string{"response": responseText}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func quickInsightsHandler(w http.ResponseWriter, r *http.Request) {
    log.Println("quickInsightsHandler called")
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{
      "insights": [
        {
          "type": "net_worth",
          "title": "Net Worth",
          "value": "₹1,721,734",
          "subtitle": "Across all accounts"
        },
        {
          "type": "monthly_spend",
          "title": "Monthly Spend",
          "value": "₹50,000",
          "subtitle": "This month"
        },
        {
          "type": "credit_score",
          "title": "Credit Score",
          "value": "750",
          "subtitle": "Excellent"
        }
      ],
      "quick_actions": [
        {
          "label": "Show my recent transactions",
          "query": "Show my recent transactions"
        },
        {
          "label": "How is my portfolio performing?",
          "query": "How is my portfolio performing?"
        }
      ],
      "timestamp": "2025-10-12T12:00:00Z"
    }`))
}

// ————— auth wrapper —————
func withAuth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        c, err := r.Cookie("sessionid")
        if err != nil {
            http.Error(w, "login required", http.StatusUnauthorized)
            return
        }
        phone := authMW.GetPhoneNumber(c.Value)
        if phone == "" {
            http.Error(w, "login required", http.StatusUnauthorized)
            return
        }
        ctx := context.WithValue(r.Context(), "phone", phone)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// ————— generic JSON file server —————
func apiHandler(fileName string) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        phone := r.Context().Value("phone").(string)
        data, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/%s", phone, fileName))
        if err != nil {
            http.Error(w, "data not found", http.StatusInternalServerError)
            return
        }
        w.Header().Set("Content-Type", "application/json")
        w.Write(data)
    })
}

// ————— SSE helper —————
func sseStream(fileName string, interval time.Duration) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        phone := r.Context().Value("phone").(string)
        w.Header().Set("Content-Type", "text/event-stream")
        w.Header().Set("Cache-Control", "no-cache")
        w.Header().Set("Connection", "keep-alive")

        fl, ok := w.(http.Flusher)
        if !ok {
            http.Error(w, "streaming unsupported", http.StatusInternalServerError)
            return
        }
        ticker := time.NewTicker(interval)
        defer ticker.Stop()

        for {
            select {
            case <-r.Context().Done():
                return
            case <-ticker.C:
                data, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/%s", phone, fileName))
                if err != nil {
                    log.Println("read error:", err)
                    continue
                }
                fmt.Fprintf(w, "data: %s\n\n", data)
                fl.Flush()
            }
        }
    })
}

// ————— Login UI handlers (unchanged) —————
func webPageHandler(w http.ResponseWriter, r *http.Request) {
    sid := r.URL.Query().Get("sessionId")
    if sid == "" {
        http.Error(w, "sessionId is required", http.StatusBadRequest)
        return
    }
    tmpl, _ := template.ParseFiles("static/login.html")
    data := struct {
        SessionId string
        Allowed   []string
    }{sid, pkg.GetAllowedMobileNumbers()}
    tmpl.Execute(w, data)
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    r.ParseForm()
    log.Printf("Request form: %v", r.Form)
    sid := r.FormValue("sessionId")
    ph := r.FormValue("phoneNumber")
    if sid == "" || ph == "" {
        http.Error(w, "sessionId & phoneNumber required", http.StatusBadRequest)
        return
    }
    authMW.AddSession(sid, ph)
    http.SetCookie(w, &http.Cookie{Name: "sessionid", Value: sid, Path: "/", SameSite: http.SameSiteLaxMode})
    tmpl, _ := template.ParseFiles("static/login_successful.html")
    tmpl.Execute(w, nil)
}