#!/usr/bin/env python3
"""
Simple test script for the News Summarizer
Run this to test the summarizer with your own article text
"""

from news_summarizer import NewsArticleSummarizer

def test_with_custom_article():
    """Test the summarizer with user input"""

    print("🗞️  News Article Summarizer - Interactive Test")
    print("=" * 50)
    print("Paste your news article text below (press Enter twice when done):")
    print()

    # Get user input
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "" and lines:
                break
            lines.append(line)
        except KeyboardInterrupt:
            print("\nTest cancelled.")
            return

    article_text = "\n".join(lines)

    if not article_text.strip():
        print("No article text provided. Using default example.")
        article_text = """
        Microsoft announced today that it will be releasing a new version of Windows
        with enhanced AI capabilities. The Windows 12 operating system will feature
        integrated ChatGPT-like functionality directly in the desktop environment.
        Microsoft CEO Satya Nadella revealed during the developer conference that
        the new OS will be available for beta testing next quarter. The company
        expects this to revolutionize how users interact with their computers.
        Industry experts predict this could be Microsoft's biggest OS launch since
        Windows 10. The new system will also include improved security features
        and better performance optimization. Microsoft's stock price increased
        5% following the announcement.
        """

    print("\n🔄 Processing your article...")
    print("(This may take a few moments)\n")

    # Initialize summarizer
    try:
        summarizer = NewsArticleSummarizer()

        # Generate summary
        summary = summarizer.summarize_article(article_text)

        print("✅ Summary Generated!")
        print("=" * 50)
        print()
        print(summary)
        print()
        print("=" * 50)
        print("Done! You can now copy and use this summary.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please make sure all dependencies are installed correctly.")

def test_with_predefined_examples():
    """Test with some predefined examples"""

    examples = [
        {
            "title": "Tech News Example",
            "text": """
            Tesla announced today that it will be releasing a new electric vehicle model
            with unprecedented range capabilities. The Model S Plaid+ will feature a
            520-mile range on a single charge, making it the longest-range production
            electric vehicle ever created. Tesla CEO Elon Musk revealed during the
            earnings call that the new vehicle will be available starting next year.
            The company expects strong demand given the current interest in sustainable
            transportation. Industry analysts predict this could accelerate the adoption
            of electric vehicles globally. The new model will also include Tesla's
            latest autopilot technology and improved interior design. Tesla's stock
            price rose 8% following the announcement.
            """
        },
        {
            "title": "Sports News Example",
            "text": """
            The NBA announced today that it will be expanding the league to include
            two new teams starting in the 2025-2026 season. The expansion will add
            franchises in Seattle and Las Vegas, bringing the total number of teams
            to 32. NBA Commissioner Adam Silver revealed during the press conference
            that the league has been considering expansion for several years. The
            decision comes after record-breaking viewership and revenue numbers.
            Basketball fans in both cities have been eagerly awaiting the return
            of professional basketball. The new teams will participate in an
            expansion draft to build their rosters. Season ticket sales are
            expected to begin later this year.
            """
        },
        {
            "title": "From food to cars: What Americans could pay more for from Trump's steel and aluminum tariffs",
            "text": """
            <span></span> <span>CNN</span>  <p> It's easy for Americans to think President Donald Trump's aluminum and steel tariffs won't affect them. Most of us aren't shopping for raw metals, after all. Yet <a href="https://www.cnn.com/2025/03/12/economy/trump-steel-aluminum-tariffs-hnk-intl/index.html">the 25% tariffs</a> rolled out on Wednesday could still manage to dent consumers' wallets.   </p> <p> From cans for food, beer and soda to cars and much, much more, steel and aluminum are used in innumerable consumer products. And much of that steel and aluminum comes from abroad, which means companies could pass on the cost of tariffs to American shoppers. </p> <p> While it's still too early for CEOs to say exactly how the tariffs will change their cost structures and, as a result, the prices they charge customers, several have already warned price hikes could soon follow. </p> <h2> Food</h2> <p> Campbell's Company CEO Mick Beekhuizen said the food and beverage maker imports steel from Canada to make cans. </p> <p> We're closely working with our suppliers to mitigate potential impact, he said on the company's earnings call this month. At the same time, depending on how long these tariffs would be in place as well as the extent of the tariffs, we might need to take other actions. That, he said, could lead to a review of pricing for some of our products. </p>  <a href="/2025/03/12/economy/trump-steel-aluminum-tariffs-hnk-intl">    <img src="https://media.cnn.com/api/v1/images/stellar/prod/gettyimages-2201391523.jpg?c=16x9&amp;q=h_144,w_256,c_fill" width="100%" />    <span>This picture taken on February 25, 2025 shows workers transporting aluminium rods at an aluminium-base material factory in Binzhou, in eastern China's Shandong province.</span>  AFP/Getty Images    <p> <span>Related article</span> <span>Trump imposes sweeping 25% steel and aluminum tariffs. Canada and Europe swiftly retaliate</span> </p> </a> <p> (Campbell's declined to share further details with CNN on how the steel and aluminum tariffs could impact consumer prices.) </p> <p> In some cases, companies could seek alternatives to aluminum or steel for packaging. For instance, Coca-Cola CEO James Quincey said last month that the company is preparing to package more of its products in <a href="https://www.cnn.com/2025/03/02/business/coke-aluminum-cans-tariffs/index.html">plastic and glass</a> as opposed to aluminum to avoid the higher input costs if the tariffs were to go into effect. </p> <p> But he cautioned outsiders may be exaggerating the impact of the 25% increase in the aluminum price relative to the total system. It's not insignificant, but it's not going to radically change a multibillion dollar US business. Still, Quincey said, It would be better not to have (the tariff). </p> <h2> Cars</h2> <p> A single car can contain hundreds, if not thousands, of pounds of steel and aluminum. </p> <p> But, for the immediate future, car manufacturers may be <a href="https://www.cnn.com/2025/02/10/politics/tariffs-steel-aluminum-trump/index.html">insulated from the tariffs</a> because they often lock rates in multi-year contracts. </p> <p> For instance, General Motors chief financial officer Paul Jacobson said on the automaker's earnings call last month that a significant amount of the steel it sources, which is primarily made in the US, is priced at relatively fixed rates for a few years. However, GM isn't shielded from market spikes in commodity prices because of the tariffs, he said. There's probably going to be an increase in costs related to market prices, but that should subside over time. </p> <h2> Appliances</h2> <p> Appliances, such as refrigerators, HVAC systems, washing machines and dryers, also require significant amounts of steel and aluminum and could become more expensive as a result of the tariffs. </p> <p> Whirlpool senior vice president controller Roxanne Warner said recently that the majority of the company's raw materials, such as steel, have locked-in contracts for a minimum of one year. </p>  <img src="https://media.cnn.com/api/v1/images/stellar/prod/ap25035653615157.jpg?q=w_1110,c_fill" width="100%" />    <span>A man walks past washing machines at a Home Depot. Such appliances could cost more after President Donald Trump imposed 25% steel and aluminum tariffs.</span>  Anthony Behar/Sipa USA/AP   <p> We also believe that given that we are producing 80% of what we sell in the US… that we are in a pretty good position (with regard to tariffs), she added, speaking at a Raymond James investor conference this month. </p> <p> At the same time, when Trump slapped a 25% tariff on steel and a 10% tariff on aluminum in 2018 with some exceptions, <a href="https://www.cnn.com/2018/10/24/business/whirlpool-earnings-trade/index.html">Whirlpool reported</a> that it saw prices of raw materials surge, raising its costs by $350 million. </p> <p> Approximately 96% of the steel used in our US factories is sourced from domestic suppliers, a Whirlpool spokesperson told CNN in an emailed statement. Still, we understand there will be implications, and we will be evaluating the overall impact relative to the recent US trade decisions and any further actions by its trade partners. </p> <p> Whirlpool did not respond to CNN's question about whether the share of US steel it uses has changed since 2018. It also did not specify the share of US aluminum used in products manufactured in the US. </p> <h2> Water</h2> <p> Water filtration systems are built using those metals, meaning even tap water could get more expensive as a result of the tariffs. </p> <p> John Stauch, the CEO of Pentair, a water treatment company that manufactures municipal equipment used to deliver potable water to homes and businesses, said the company purchases $100 million worth of aluminum and steel from outside the US. </p> <p> Additionally, Stauch said Pentair purchases $125 million worth of components from China, where non-steel or aluminum goods coming to the US are already being tariffed at 20%. So in total, the tariffs currently in place are costing them $50 million, he said. </p> <p> Effective April 1 and April 15, we're planning to go with price increases across the businesses, he said at a JPMorgan industry conference on Tuesday. </p> <p> As water filtration costs rise, providers could pass along the price to consumers by billing them higher rates. </p> <p> I'm guessing we're generally all in the same playing field, Stauch added, referring to water filtration competitors. Generally, what we'd be doing is across-the-board price increases, and therefore working to sell the product that we can make the most amount of profit for. </p>
            """
        }
    ]

    print("🗞️  News Article Summarizer - Predefined Examples")
    print("=" * 50)

    summarizer = NewsArticleSummarizer()

    for i, example in enumerate(examples, 1):
        print(f"\n📰 Example {i}: {example['title']}")
        print("-" * 40)

        summary = summarizer.summarize_article(example['text'])
        print(summary)
        print()

def main():
    """Main function to choose test mode"""

    print("Welcome to the News Summarizer Test!")
    print("Choose an option:")
    print("1. Test with your own article text")
    print("2. Test with predefined examples")
    print("3. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                test_with_custom_article()
                break
            elif choice == "2":
                test_with_predefined_examples()
                break
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
