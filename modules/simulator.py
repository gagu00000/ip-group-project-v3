# ============================================================================
# PAGE: SIMULATOR - ENHANCED VERSION WITH DETAILED BREAKDOWN
# ============================================================================

def show_simulator_page():
    st.markdown('<h1 class="page-title page-title-purple">🎯 Campaign Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Run what-if scenarios and forecast campaign outcomes</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Please load data first.")
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-cyan">⚙️ Campaign Parameters</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p style="color: var(--accent-cyan); font-weight: 700;">💰 Pricing</p>', unsafe_allow_html=True)
        discount_pct = st.slider("Discount %", 0, 50, 15, help="Discount to offer customers")
        promo_budget = st.number_input("Promo Budget (AED)", 1000, 500000, 25000, step=5000, help="Total campaign budget")
    
    with col2:
        st.markdown('<p style="color: var(--accent-purple); font-weight: 700;">📊 Constraints</p>', unsafe_allow_html=True)
        margin_floor = st.slider("Margin Floor %", 0, 50, 15, help="Minimum acceptable profit margin")
        campaign_days = st.slider("Campaign Days", 1, 30, 7, help="Duration of promotional campaign")
    
    with col3:
        st.markdown('<p style="color: var(--accent-pink); font-weight: 700;">🎯 Targeting</p>', unsafe_allow_html=True)
        
        cities = ['All'] + (sorted(stores_df['city'].dropna().unique().tolist()) if stores_df is not None and 'city' in stores_df.columns else [])
        channels = ['All'] + (sorted(stores_df['channel'].dropna().unique().tolist()) if stores_df is not None and 'channel' in stores_df.columns else [])
        categories = ['All'] + (sorted(products_df['category'].dropna().unique().tolist()) if products_df is not None and 'category' in products_df.columns else [])
        
        city = st.selectbox("Target City", cities)
        channel = st.selectbox("Target Channel", channels)
        category = st.selectbox("Target Category", categories)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_simulation = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
    if run_simulation:
        with st.spinner("🔄 Running simulation..."):
            try:
                sim = Simulator()
                results = sim.simulate_campaign(
                    sales_df, stores_df, products_df,
                    discount_pct=discount_pct,
                    promo_budget=promo_budget,
                    margin_floor=margin_floor,
                    city=city,
                    channel=channel,
                    category=category,
                    campaign_days=campaign_days
                )
                st.session_state.sim_results = results
                st.session_state.sim_params = {
                    'discount_pct': discount_pct,
                    'promo_budget': promo_budget,
                    'margin_floor': margin_floor,
                    'campaign_days': campaign_days,
                    'city': city,
                    'channel': channel,
                    'category': category
                }
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # ===== DISPLAY RESULTS =====
    if 'sim_results' in st.session_state and st.session_state.sim_results:
        results = st.session_state.sim_results
        outputs = results.get('outputs')
        comparison = results.get('comparison')
        warnings = results.get('warnings', [])
        params = st.session_state.get('sim_params', {})
        
        if outputs:
            st.markdown("---")
            
            # ===== MAIN KPI CARDS =====
            st.markdown('<p class="section-title section-title-teal">📊 Campaign Results</p>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rev_delta = f"{comparison['revenue_change_pct']:+.1f}%"
                st.markdown(create_metric_card(
                    "Expected Revenue", 
                    format_currency(outputs['expected_revenue']), 
                    rev_delta, 
                    "positive" if comparison['revenue_change_pct'] > 0 else "negative", 
                    "cyan"
                ), unsafe_allow_html=True)
            
            with col2:
                order_delta = f"{comparison['order_change_pct']:+.1f}%"
                st.markdown(create_metric_card(
                    "Expected Orders", 
                    f"{outputs['expected_orders']:,}", 
                    order_delta, 
                    "positive" if comparison['order_change_pct'] > 0 else "negative", 
                    "blue"
                ), unsafe_allow_html=True)
            
            with col3:
                profit_delta = f"{comparison['profit_change_pct']:+.1f}%"
                st.markdown(create_metric_card(
                    "Gross Profit", 
                    format_currency(outputs.get('expected_gross_profit', outputs['expected_net_profit'])), 
                    profit_delta, 
                    "positive" if comparison['profit_change_pct'] > 0 else "negative", 
                    "green"
                ), unsafe_allow_html=True)
            
            with col4:
                roi_color = "green" if outputs['roi_pct'] > 0 else "pink"
                st.markdown(create_metric_card(
                    "ROI", 
                    f"{outputs['roi_pct']:.1f}%", 
                    color=roi_color
                ), unsafe_allow_html=True)
            
            # ===== WARNINGS =====
            if warnings:
                st.markdown("<br>", unsafe_allow_html=True)
                for w in warnings:
                    st.warning(w)
            else:
                st.success("✅ Campaign looks healthy!")
            
            st.markdown("---")
            
            # ===== DETAILED BREAKDOWN - NEW SECTION =====
            st.markdown('<p class="section-title section-title-purple">📋 Detailed Calculation Breakdown</p>', unsafe_allow_html=True)
            
            # Two column layout for breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Baseline Performance (Without Campaign)")
                st.markdown(f"""
                <div class="info-card">
                    <table style="width: 100%; color: var(--text-primary);">
                        <tr>
                            <td style="padding: 8px 0;">📈 Baseline Revenue ({params.get('campaign_days', 7)} days)</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-cyan);">{format_currency(comparison['baseline_revenue'])}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">📦 Baseline Orders</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-blue);">{comparison['baseline_orders']:,}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">💰 Baseline Profit</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-green);">{format_currency(comparison['baseline_profit'])}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🎯 Campaign Parameters Used")
                st.markdown(f"""
                <div class="info-card" style="border-left-color: var(--accent-purple);">
                    <table style="width: 100%; color: var(--text-primary);">
                        <tr>
                            <td style="padding: 8px 0;">🏷️ Discount</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-pink);">{params.get('discount_pct', 0)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">💵 Budget</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-orange);">{format_currency(params.get('promo_budget', 0))}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">📅 Duration</td>
                            <td style="text-align: right; font-weight: bold;">{params.get('campaign_days', 7)} days</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">🎯 Target</td>
                            <td style="text-align: right; font-weight: bold;">{params.get('city', 'All')} / {params.get('channel', 'All')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🚀 Campaign Effect (With Promotion)")
                
                # Calculate incremental values
                incremental_revenue = outputs['expected_revenue'] - comparison['baseline_revenue']
                incremental_profit = outputs.get('expected_gross_profit', outputs['expected_net_profit']) - comparison['baseline_profit']
                incremental_orders = outputs['expected_orders'] - comparison['baseline_orders']
                
                st.markdown(f"""
                <div class="success-card">
                    <table style="width: 100%; color: var(--text-primary);">
                        <tr>
                            <td style="padding: 8px 0;">📈 Expected Revenue</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-cyan);">{format_currency(outputs['expected_revenue'])}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">📦 Expected Orders</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-blue);">{outputs['expected_orders']:,}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">💰 Gross Profit</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-green);">{format_currency(outputs.get('expected_gross_profit', outputs['expected_net_profit']))}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">📊 Profit Margin</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-purple);">{outputs.get('expected_margin_pct', 0):.1f}%</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📈 Incremental Gain")
                st.markdown(f"""
                <div class="info-card" style="border-left-color: var(--accent-green);">
                    <table style="width: 100%; color: var(--text-primary);">
                        <tr>
                            <td style="padding: 8px 0;">➕ Extra Revenue</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-cyan);">{format_currency(incremental_revenue)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">➕ Extra Orders</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-blue);">+{incremental_orders:,}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">➕ Extra Profit</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-green);">{format_currency(incremental_profit)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">📊 Volume Uplift</td>
                            <td style="text-align: right; font-weight: bold; color: var(--accent-purple);">+{outputs.get('demand_lift_pct', 0):.1f}%</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ===== ROI CALCULATION EXPLAINED =====
            st.markdown('<p class="section-title section-title-orange">🧮 ROI Calculation Explained</p>', unsafe_allow_html=True)
            
            promo_spend = outputs.get('promo_cost', params.get('promo_budget', 0) * 0.3)
            gross_profit = outputs.get('expected_gross_profit', outputs['expected_net_profit'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="info-card" style="border-left-color: var(--accent-orange);">
                    <h4 style="color: var(--accent-orange); margin-bottom: 15px;">📐 ROI Formula</h4>
                    <div style="background: var(--bg-tertiary); padding: 15px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; color: var(--text-primary);">
                        <p style="margin: 5px 0;">ROI = (Gross Profit - Promo Spend) / Promo Spend × 100</p>
                        <hr style="border-color: var(--border-default); margin: 10px 0;">
                        <p style="margin: 5px 0;">ROI = ({format_currency(gross_profit)} - {format_currency(promo_spend)}) / {format_currency(promo_spend)} × 100</p>
                        <hr style="border-color: var(--border-default); margin: 10px 0;">
                        <p style="margin: 5px 0; color: var(--accent-green); font-weight: bold;">ROI = {outputs['roi_pct']:.1f}%</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="info-card" style="border-left-color: var(--accent-teal);">
                    <h4 style="color: var(--accent-teal); margin-bottom: 15px;">💡 What This Means</h4>
                    <div style="color: var(--text-primary); line-height: 1.8;">
                        <p>• For every <strong>AED 1</strong> spent on this campaign</p>
                        <p>• You generate <strong>AED {(gross_profit / promo_spend):.2f}</strong> in gross profit</p>
                        <p>• Net return: <strong>AED {((gross_profit - promo_spend) / promo_spend):.2f}</strong> per AED spent</p>
                        <hr style="border-color: var(--border-default); margin: 10px 0;">
                        <p style="color: var(--accent-green);">✅ ROI > 100% = Campaign is highly profitable</p>
                        <p style="color: var(--accent-orange);">⚠️ ROI 0-100% = Campaign breaks even or small gain</p>
                        <p style="color: var(--accent-red);">❌ ROI < 0% = Campaign loses money</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ===== COMPARISON CHARTS =====
            st.markdown('<p class="section-title section-title-blue">📈 Visual Comparison</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart: Baseline vs Campaign
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Baseline (No Promo)',
                    x=['Revenue', 'Profit', 'Orders'],
                    y=[comparison['baseline_revenue'], comparison['baseline_profit'], comparison['baseline_orders'] * 1000],
                    marker_color='#3b82f6',
                    text=[format_currency(comparison['baseline_revenue']), 
                          format_currency(comparison['baseline_profit']), 
                          f"{comparison['baseline_orders']:,}"],
                    textposition='outside'
                ))
                
                fig.add_trace(go.Bar(
                    name='With Campaign',
                    x=['Revenue', 'Profit', 'Orders'],
                    y=[outputs['expected_revenue'], 
                       outputs.get('expected_gross_profit', outputs['expected_net_profit']), 
                       outputs['expected_orders'] * 1000],
                    marker_color='#06b6d4',
                    text=[format_currency(outputs['expected_revenue']), 
                          format_currency(outputs.get('expected_gross_profit', outputs['expected_net_profit'])), 
                          f"{outputs['expected_orders']:,}"],
                    textposition='outside'
                ))
                
                fig = style_plotly_chart_themed(fig, height=400)
                fig.update_layout(
                    barmode='group', 
                    title='Baseline vs Campaign Performance',
                    yaxis_title='Value (AED / Orders×1000)',
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Waterfall chart: Profit breakdown
                fig_waterfall = go.Figure(go.Waterfall(
                    name="Profit Breakdown",
                    orientation="v",
                    measure=["absolute", "relative", "relative", "relative", "total"],
                    x=["Baseline Profit", "Volume Uplift", "Price Discount", "Promo Cost", "Final Profit"],
                    y=[
                        comparison['baseline_profit'],
                        incremental_profit + (comparison['baseline_profit'] * params.get('discount_pct', 0) / 100),
                        -(comparison['baseline_profit'] * params.get('discount_pct', 0) / 100),
                        -promo_spend,
                        outputs.get('expected_gross_profit', outputs['expected_net_profit']) - promo_spend
                    ],
                    connector={"line": {"color": "#475569"}},
                    decreasing={"marker": {"color": "#ef4444"}},
                    increasing={"marker": {"color": "#10b981"}},
                    totals={"marker": {"color": "#8b5cf6"}}
                ))
                
                fig_waterfall = style_plotly_chart_themed(fig_waterfall, height=400)
                fig_waterfall.update_layout(title="Profit Bridge: How Campaign Affects Profit", showlegend=False)
                st.plotly_chart(fig_waterfall, use_container_width=True)
            
            st.markdown("---")
            
            # ===== SENSITIVITY ANALYSIS =====
            st.markdown('<p class="section-title section-title-pink">🎚️ Sensitivity Analysis: What If?</p>', unsafe_allow_html=True)
            
            # Calculate ROI at different discount levels
            discount_levels = [5, 10, 15, 20, 25, 30]
            sim = Simulator()
            
            sensitivity_data = []
            for disc in discount_levels:
                test_results = sim.simulate_campaign(
                    sales_df, stores_df, products_df,
                    discount_pct=disc,
                    promo_budget=params.get('promo_budget', 25000),
                    margin_floor=params.get('margin_floor', 15),
                    city=params.get('city', 'All'),
                    channel=params.get('channel', 'All'),
                    category=params.get('category', 'All'),
                    campaign_days=params.get('campaign_days', 7)
                )
                if test_results['outputs']:
                    sensitivity_data.append({
                        'Discount %': disc,
                        'Revenue': test_results['outputs']['expected_revenue'],
                        'Profit': test_results['outputs'].get('expected_gross_profit', test_results['outputs']['expected_net_profit']),
                        'ROI %': test_results['outputs']['roi_pct'],
                        'Margin %': test_results['outputs'].get('expected_margin_pct', 0)
                    })
            
            if sensitivity_data:
                sens_df = pd.DataFrame(sensitivity_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Line chart: ROI vs Discount
                    fig_sens = go.Figure()
                    fig_sens.add_trace(go.Scatter(
                        x=sens_df['Discount %'],
                        y=sens_df['ROI %'],
                        mode='lines+markers',
                        name='ROI %',
                        line=dict(color='#8b5cf6', width=3),
                        marker=dict(size=10)
                    ))
                    
                    # Highlight current selection
                    current_disc = params.get('discount_pct', 15)
                    current_row = sens_df[sens_df['Discount %'] == current_disc]
                    if len(current_row) > 0:
                        fig_sens.add_trace(go.Scatter(
                            x=[current_disc],
                            y=[current_row['ROI %'].values[0]],
                            mode='markers',
                            name='Your Selection',
                            marker=dict(size=20, color='#ec4899', symbol='star')
                        ))
                    
                    fig_sens = style_plotly_chart_themed(fig_sens, height=350)
                    fig_sens.update_layout(title='ROI at Different Discount Levels', xaxis_title='Discount %', yaxis_title='ROI %')
                    st.plotly_chart(fig_sens, use_container_width=True)
                
                with col2:
                    # Table
                    st.markdown("#### 📊 Discount Comparison Table")
                    
                    # Format the dataframe
                    display_df = sens_df.copy()
                    display_df['Revenue'] = display_df['Revenue'].apply(lambda x: format_currency(x))
                    display_df['Profit'] = display_df['Profit'].apply(lambda x: format_currency(x))
                    display_df['ROI %'] = display_df['ROI %'].apply(lambda x: f"{x:.1f}%")
                    display_df['Margin %'] = display_df['Margin %'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                    # Find optimal discount
                    optimal_idx = sens_df['ROI %'].idxmax()
                    optimal_disc = sens_df.loc[optimal_idx, 'Discount %']
                    optimal_roi = sens_df.loc[optimal_idx, 'ROI %']
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-title">💡 Optimal Discount</div>
                        <div class="insight-text">Based on this analysis, <strong>{optimal_disc}% discount</strong> gives the best ROI of <strong>{optimal_roi:.1f}%</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ===== RECOMMENDATIONS =====
            st.markdown('<p class="section-title section-title-green">💡 Recommendations</p>', unsafe_allow_html=True)
            
            recommendations = []
            
            # ROI-based recommendations
            if outputs['roi_pct'] > 200:
                recommendations.append("🎯 **Excellent ROI!** This campaign is highly profitable. Consider scaling up the budget.")
            elif outputs['roi_pct'] > 100:
                recommendations.append("✅ **Good ROI.** Campaign is profitable. Monitor execution closely.")
            elif outputs['roi_pct'] > 0:
                recommendations.append("⚠️ **Marginal ROI.** Campaign is barely profitable. Consider reducing discount or budget.")
            else:
                recommendations.append("❌ **Negative ROI.** Campaign will lose money. Reduce discount or reconsider strategy.")
            
            # Margin-based recommendations
            margin = outputs.get('expected_margin_pct', 0)
            if margin < params.get('margin_floor', 15):
                recommendations.append(f"⚠️ **Margin Alert:** Expected margin ({margin:.1f}%) is below your floor ({params.get('margin_floor', 15)}%). Reduce discount.")
            elif margin > 30:
                recommendations.append(f"💰 **Healthy Margin:** At {margin:.1f}%, there's room for deeper discounts if needed.")
            
            # Volume recommendations
            if outputs.get('demand_lift_pct', 0) < 10:
                recommendations.append("📦 **Low Volume Lift:** Consider increasing discount to drive more traffic.")
            elif outputs.get('demand_lift_pct', 0) > 50:
                recommendations.append("📦 **High Volume Lift:** Ensure inventory can handle the demand surge.")
            
            for rec in recommendations:
                st.markdown(f'<div class="recommendation-card"><p>{rec}</p></div>', unsafe_allow_html=True)
    
    show_footer()
